package io.nikolai.san.service

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import io.nikolai.san.state.ShopperStateMachine
import io.nikolai.san.comm.NikolaiBroker

class ShopperAccessibilityService : AccessibilityService() {

    private val stateMachine = ShopperStateMachine()
    private val broker = NikolaiBroker()

    override fun onServiceConnected() {
        // Dynamic configuration for performance
        serviceInfo.apply {
            eventTypes = AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED or
                         AccessibilityEvent.TYPE_VIEW_SCROLLED or
                         AccessibilityEvent.TYPE_VIEW_CLICKED
            feedbackType = AccessibilityService.FEEDBACK_GENERIC
            flags = AccessibilityService.FLAG_RETRIEVE_INTERACTIVE_WINDOWS or
                    AccessibilityService.FLAG_REPORT_VIEW_IDS
        }
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent) {
        val rootNode = rootInActiveWindow ?: return
        
        when (event.eventType) {
            AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED -> {
                stateMachine.handleWindowState(event, rootNode)
            }
            AccessibilityEvent.TYPE_VIEW_SCROLLED -> {
                // Sync with auto-scroll extraction
            }
        }
        rootNode.recycle()
    }

    override fun onInterrupt() {}
}
