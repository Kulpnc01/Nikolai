---
title: "Shopper Assistant Node (SAN) — Technical Architecture Specification"
version: "1.0"
author: "Nicholas"
status: "Draft"
document_type: "Technical Specification"
---

# Shopper Assistant Node (SAN) — Technical Architecture Specification

- [1. Executive Summary](#1-executive-summary)
- [2. System Overview](#2-system-overview)
- [3. Accessibility Architecture](#3-accessibility-architecture)
- [4. Shopper App State Machine](#4-shopper-app-state-machine)
- [5. Data Extraction and OCR Pipeline](#5-data-extraction-and-ocr-pipeline)
- [6. Communication Layer and Nikolai Integration](#6-communication-layer-and-nikolai-integration)
- [7. Wearables and Bluetooth Architecture](#7-wearables-and-bluetooth-architecture)
- [8. Media Streaming and Head Unit Integration](#8-media-streaming-and-head-unit-integration)
- [9. Security and Privacy Model](#9-security-and-privacy-model)
- [10. Implementation Roadmap](#10-implementation-roadmap)
- [11. Appendices](#11-appendices)

## 1. Executive Summary

The Shopper Assistant Node (SAN) is designed to alleviate the extreme cognitive and physical demands placed on gig-economy fulfillment operators, specifically within platforms like Shipt. The contemporary shopper must navigate complex retail environments while simultaneously managing deeply nested digital interfaces and real-time client communications. This constant context-switching creates a high cognitive load that impacts efficiency and safety.

The SAN operates as an autonomous edge-computing proxy on Android, bridging the gap between physical retail execution and an external high-order cognitive system named "Nikolai." By utilizing Android's AccessibilityService and MediaProjection APIs, the node creates a local-first, low-latency interface capable of environmental interaction without requiring manual input.

Key capabilities include background UI introspection, hybrid data extraction (Accessibility Tree + OCR), secure peer-to-peer communication via Tailscale/WireGuard, and multimodal output via AR overlays, wearable haptics, and vehicle head-unit streaming. This system transforms the shopper from a manual data entry operator into a high-level logistical supervisor assisted by real-time intelligence.

## 2. System Overview

The SAN architecture is a distributed system consisting of the Android mobile node, a Linux-based cognitive core (Nikolai), and various peripheral interfaces.

### High-Level Architecture Diagram

```text
+-----------------------------------------------------------+
| Android SAN (Mobile Node)                                 |
| +-------------------+       +---------------------------+ |
| | Accessibility     |       | OCR Pipeline (PaddleOCR)  | |
| | Service           |       | (ONNX Runtime)            | |
| +---------+---------+       +-------------+-------------+ |
|           |                               |               |
|           +---------------+---------------+               |
|                           |                               |
|             +-------------v-------------+                 |
|             | State Machine & IPC Broker|                 |
|             +-------------+-------------+                 |
|                           |                               |
|             +-------------v-------------+                 |
|             | Termux + Tailscale Proxy  |                 |
|             +-------------+-------------+                 |
+---------------------------|-------------------------------+
                            | (WireGuard Tunnel)
                            v
+---------------------------+-------------------------------+
| Nikolai Cognitive Core (Remote/Local)                     |
| +-------------------+       +---------------------------+ |
| | TSP Route Solver  |       | Intent Engine             | |
| +-------------------+       +---------------------------+ |
+-----------------------------------------------------------+
```

### Major Subsystems
- **Android SAN App:** The host application managing the lifecycle of background services.
- **AccessibilityService:** The primary "eyes" and "hands" of the system for UI interaction.
- **OCR Engine:** On-device PaddleOCR v5 for parsing non-textual or obfuscated UI elements.
- **Communication Layer:** A userspace Tailscale implementation within Termux for secure P2P links.
- **Nikolai:** The backend reasoning engine for route optimization and decision support.
- **Wearables/Head-Unit:** Output channels for AR navigation, haptics, and media streaming.

## 3. Accessibility Architecture

The system utilizes the `AccessibilityService` API to inspect the Shipt application's UI hierarchy and perform autonomous actions.

### 3.1 Service Configuration and Lifecycle
The service is registered with the `BIND_ACCESSIBILITY_SERVICE` permission and configured via XML/Dynamic settings.

| Method | Role |
|--------|------|
| `onServiceConnected()` | Dynamic filtering and configuration initialization. |
| `onAccessibilityEvent()` | Core entry point for processing UI changes. |
| `onInterrupt()` | Graceful halt of automation tasks. |

### 3.2 Event Filtering
To optimize battery and CPU, the service filters for specific event types:
- `TYPE_WINDOW_STATE_CHANGED`: Detection of screen transitions (e.g., Order Offer, List Loaded).
- `TYPE_VIEW_SCROLLED`: Synchronization with programmatic scrolling.
- `TYPE_VIEW_CLICKED`: Tracking operator progress and confirmation.

### 3.3 Dynamic List Extraction (RecyclerView Traversal)
Since `RecyclerView` recycles off-screen nodes, the SAN implements an autonomous scrolling loop to extract full shopping lists.

```java
// Logic: Scroll -> Capture -> Hash -> Deduplicate -> Repeat
while (!isAtEndOfList) {
    List<AccessibilityNodeInfo> visible = extractNodes(root);
    for (node : visible) {
        String hash = generateDeterministicHash(node);
        if (uniqueSet.add(hash)) { items.add(node); }
    }
    if (noNewItemsFound) isAtEndOfList = true;
    else scrollForward(recyclerView);
}
```

## 4. Shopper App State Machine

The SAN's behavior is governed by a deterministic state machine to ensure safe and predictable UI interaction.

### 4.1 State Transition Matrix

| Current State | Trigger Event | Next State | System Action |
|---------------|---------------|------------|---------------|
| **IDLE** | Order Offer detected | **ORDER_NOTIFICATION** | Analyze payout/items; Send to Nikolai. |
| **ORDER_NOTIFICATION** | Nikolai "ACCEPT" command | **ORDER_ACCEPTANCE** | Dispatch `ACTION_CLICK` on the identified "Claim" button node. |
| **ORDER_ACCEPTANCE** | List UI loaded | **LIST_EXTRACTION** | Initialize RecyclerView traversal and trigger OCR fallback routines for obfuscated data. |
| **LIST_EXTRACTION** | Traversal completes | **STORE_NAVIGATION** | Transmit normalized Protobuf payload to Nikolai. Await TSP-optimized route map. |
| **STORE_NAVIGATION** | Operator enters specific aisle geofence | **ITEM_CONFIRMATION** | Display floating overlay for current item. Trigger localized BLE haptic cues. |
| **ITEM_CONFIRMATION** | Item "Found" clicked | **STORE_NAVIGATION** | Proceed to next item in TSP route. |
| **ERROR_RECOVERY** | Substitution dialog detected | **STORE_NAVIGATION** | Nikolai selects optimal sub based on customer data; Auto-click selection. |

### 4.2 State Transition Diagram

```text
[IDLE] --(Order Offer)--> [ORDER_NOTIFICATION]
      \                        |
       \---(Nikolai Accept)----v
                               [ORDER_ACCEPTANCE] --(List Loaded)--> [LIST_EXTRACTION]
                                     |                                     |
                                     |<---------(Traversal End)------------+
                                     v
                               [STORE_NAVIGATION] <--(Geofence)--> [ITEM_CONFIRMATION]
                                     |                                     ^
                                     +--(Substitution)--> [ERROR_RECOVERY]-+
```

## 5. Data Extraction and OCR Pipeline

The SAN employs a hybrid strategy to extract structured data from unstructured or obfuscated graphical layouts.

### 5.1 Extraction Targets
- **Item Metadata:** Name, brand, SKU.
- **Volumetric Data:** Quantity, weights, substitution limits.
- **Spatial Data:** Aisle numbers, department, shelf location.

### 5.2 Hybrid Strategy
1. **Depth-First Tree Parsing:** Primary extraction using `AccessibilityNodeInfo` hierarchy.
2. **Heuristic/Regex Validation:** Linking quantity (e.g., `^\d+\s*ct$`) to the nearest product name via spatial proximity.
3. **OCR Fallback (PaddleOCR v5):** Used when UI elements lack accessibility semantics or use custom Canvas rendering.

### 5.3 On-Device OCR Architecture
The system utilizes **PaddleOCR v5** via ONNX Runtime for high-fidelity layout preservation.
- **Detector:** Differentiable Binarization (DB).
- **Recognition:** SVTR (Single-line Visual Text Recognition).
- **Fusion:** Coordinates from OCR are fused with Accessibility Tree nodes using Cartesian alignment to reconstruct missing relationships (e.g., Aisle images to text).

## 6. Communication Layer and Nikolai Integration

Secure, low-latency communication is achieved through a userspace Tailscale mesh.

### 6.1 Networking Stack
- **Termux Environment:** Hosts the Tailscale daemon in userspace mode.
- **Tailscale Proxy:** SOCKS5 proxy on `localhost:1055` provides an encrypted WireGuard tunnel.
- **P2P Link:** Direct UDP hole-punching between Android and Nikolai core.

### 6.2 Serialization Performance
The system mandates **Protobuf** over JSON for performance and battery conservation.

| Metric | Protobuf | JSON |
|--------|----------|------|
| Serialization Speed | ~6,500 ns/op | ~42,000 ns/op |
| Payload Size | Dense Binary | Verbose Text |
| CPU Overhead | Low (Schema-based) | High (String parsing) |

### 6.3 Resilience
An **Offline-First SQLite Queue** ensures eventual consistency. If the tailnet link is severed, the node caches all events and flushes them upon reconnection with deterministic timestamps.

## 7. Wearables and Bluetooth Architecture

The SAN acts as a BLE Peripheral to support hands-free operation.

### 7.1 Protocol Stack (GATT & L2CAP)
- **GATT Server:** Used for low-bandwidth haptic triggers and status notifications.
- **L2CAP Channels:** Connection-oriented sockets used for high-bandwidth streaming of route maps to AR glasses.

### 7.2 Connection Lifecycle

| Phase | Action |
|-------|--------|
| **Discovery** | Wearable scans for proprietary 128-bit Service UUID. |
| **Handshake** | GATT Characteristic advertises the Protocol/Service Multiplexer (PSM). |
| **Streaming** | Wearable connects to PSM via L2CAP for raw map data. |

## 8. Media Streaming and Head Unit Integration

During the delivery phase, the SAN streams navigation to the vehicle head unit using WebRTC.

### 8.1 Streaming Pipeline
1. **Capture:** `MediaProjection` API captures the navigation app window.
2. **Transport:** WebRTC P2P over the Tailscale tunnel (WireGuard).
3. **Zero-Config:** No STUN/TURN required; ICE candidates are signaled directly via Tailscale IPs.
4. **Latency:** Achieves sub-500ms latency compared to standard Miracast/RTMP.

## 9. Security and Privacy Model

The system operates with elevated privileges and follows a "Zero-Trust" edge model.

### 9.1 Core Protections
- **Local-First Processing:** OCR bitmaps are processed entirely on-device; only normalized metadata is transmitted.
- **Transport Encryption:** All traffic is encapsulated in WireGuard (ChaCha20 + Curve25519).
- **Screen Protection:** `FLAG_SECURE` is applied to internal SAN config screens to prevent third-party scraping.
- **Process Isolation:** IPC between Android App and Termux is restricted via Unix domain sockets and UID-based intent filtering.

> **Note:**
> This system possesses elevated privileges (Accessibility, MediaProjection). Any breach of the Nikolai-SAN link could expose real-time user activity. Transport security via Tailscale is non-negotiable.

## 10. Implementation Roadmap

### Phase 1: Accessibility & State Core
- **Objective:** Establish the foundation of the background service and state machine.
- **Tasks:** Implement `AccessibilityService`, define the state machine transitions, and construct the RecyclerView auto-scroll and cryptographic node hashing deduplication algorithms.
- **Testing:** Utilize Android UIAutomator to simulate the Shipt interface. Verify node traversal logic against mocked, highly nested lists ensuring zero OOM exceptions.

### Phase 2: Local Intelligence & OCR
- **Objective:** Handle edge cases and obfuscated UI elements via machine vision.
- **Tasks:** Integrate the ONNX Runtime Mobile library and deploy the PaddleOCR v5 models. Map TakeScreenshotCallback to the OCR ingestion pipeline and fuse bounding box data with accessibility text strings.
- **Testing:** Measure character error rates (CER) and verify structural layout preservation against standard Tesseract benchmarks.

### Phase 3: Communication & Nikolai Integration
- **Objective:** Bridge the physical node to the cognitive engine securely.
- **Tasks:** Instantiate the Termux userspace Tailscale proxy. Implement Protobuf serialization schemas. Establish the gRPC bidirectional link and construct the offline-first SQLite message queue.
- **Testing:** Monitor memory allocations and battery drain metrics via Android Studio Profiler. Ensure the serialization and socket polling do not violate power constraints.

### Phase 4: Wearables, Overlays, and Streaming
- **Objective:** Deploy multimodal output channels.
- **Tasks:** Build the BluetoothGattServer and L2CAP socket connection handler. Implement the SYSTEM_ALERT_WINDOW logic with lifecycle awareness to prevent foreground crashes. Construct the WebRTC MediaProjection pipeline over the tailnet.
- **Testing:** Conduct Hardware-in-the-loop (HIL) testing with physical AR glasses and Android-based vehicle head units to tune WebRTC bitrates and verify BLE L2CAP latency.

## 11. Appendices

### Appendix A: Example Protobuf Schema
```protobuf
syntax = "proto3";

// Defines a single extracted node from the UI tree
message AccessibilityNode {
  string view_id_resource_name = 1;
  string text = 2;
  string content_description = 3;
  bool is_clickable = 4;
  BoundingBox bounds_in_screen = 5;
}

// Cartesian coordinates for spatial layout analysis
message BoundingBox {
  int32 top = 1;
  int32 left = 2;
  int32 bottom = 3;
  int32 right = 4;
}

// Core payload transmitted to Nikolai
message ShopperStatePayload {
  enum State {
    IDLE = 0;
    LIST_EXTRACTION = 1;
    STORE_NAVIGATION = 2;
    ERROR_RECOVERY = 3;
    DELIVERY_NAVIGATION = 4;
  }
  State current_state = 1;
  repeated AccessibilityNode visible_nodes = 2;
  int64 timestamp = 3;
  string active_tailnet_ip = 4;
}
```

### Appendix B: Auto-Scroll Action Pseudocode
```java
// Pseudocode for traversing a dynamic RecyclerView and deduplicating items
void scrapeDynamicList(AccessibilityNodeInfo rootNode) {
    List<AccessibilityNodeInfo> allItems = new ArrayList<>();
    HashSet<String> seenHashes = new HashSet<>();
    boolean isAtEndOfList = false;

    while (!isAtEndOfList) {
        List<AccessibilityNodeInfo> visibleItems = extractTargetNodes(rootNode);
        int newItemsInCycle = 0;

        for (AccessibilityNodeInfo item : visibleItems) {
            // Generate deterministic hash based on content and spatial location
            String nodeHash = generateHash(item.getText(), item.getBoundsInScreen());
            if (!seenHashes.contains(nodeHash)) {
                seenHashes.add(nodeHash);
                allItems.add(item);
                newItemsInCycle++;
            }
        }

        if (newItemsInCycle == 0) {
            isAtEndOfList = true; // No new items found after scroll
        } else {
            // Locate the scrollable container and advance programmatically
            AccessibilityNodeInfo listNode = findScrollableNode(rootNode);
            if (listNode != null) {
                listNode.performAction(AccessibilityNodeInfo.ACTION_SCROLL_FORWARD);
                waitForEvent(AccessibilityEvent.TYPE_VIEW_SCROLLED); // Await UI update
            }
        }
    }
    transmitToNikolai(allItems);
}
```

### Appendix C: Example OCR Output vs Accessibility Node Fusion

| Element | Accessibility Tree Data | PaddleOCR v5 Extracted Data | Fused Output |
|---------|-------------------------|-----------------------------|--------------|
| Product Title | text: "Organic Whole Milk" | text: "Organic Whole Milk", conf: 0.99 | Confirmed. Primary text anchor. |
| Quantity | Null / Missing Node | text: "1 Gallon", conf: 0.98 | Quantifier fused via spatial proximity (Y-axis alignment). |
| Aisle Location | viewId: "img_aisle_map" | text: "Aisle 4, Section B", conf: 0.95 | OCR text replaces raw image node for routing logic. |

---

## Research Prompts for Further Exploration

1. "Given the SAN technical spec, propose an alternative OCR architecture that reduces on-device compute while preserving layout fidelity."
2. "Using the SAN state machine, design a fault-injection test plan that validates recovery from network loss during STORE_NAVIGATION."
3. "Based on the communication layer described, suggest a migration path from gRPC to QUIC while maintaining Protobuf payloads."
4. "Given the BLE architecture, design a protocol for AR glasses to request on-demand route summaries from the SAN."
5. "Propose a reinforcement learning model for Nikolai that optimizes 'Substitution Selection' based on the ERROR_RECOVERY state telemetry."
6. "Design a privacy-preserving 'Redaction Overlay' that uses the OCR pipeline to identify and hide customer names on the Android screen during MediaProjection."
7. "Analyze the impact of Android 15's 'Private Space' feature on the SAN's ability to bind to the Shipt AccessibilityService."
8. "Develop a power-consumption profile comparing BLE GATT notifications vs. L2CAP streaming for continuous navigation updates."
9. "Propose a deduplication algorithm for the LIST_EXTRACTION phase that handles variable-height RecyclerView items without explicit unique IDs."
10. "Design a gRPC-based health-check protocol that allows Nikolai to remotely reset the SAN state machine if 'STALL' is detected."
11. "Evaluate the feasibility of using WebGL overlays instead of standard Android Views to reduce the memory footprint of the STORE_NAVIGATION map."
12. "Describe how the SAN could utilize Android's Ultra-Wideband (UWB) APIs to improve item localization accuracy within the aisle geofence."
13. "Create a Protobuf definition for a 'Vibration Pattern' message that allows Nikolai to send custom haptic feedback sequences to BLE wearables."
14. "Suggest a method for the SAN to detect 'Physical Layout Mismatch' where the store's physical aisles do not match Nikolai's TSP route."
15. "Propose a strategy for the SAN to handle multi-window mode where Shipt and a navigation app are both visible, impacting Accessibility tree parsing."
