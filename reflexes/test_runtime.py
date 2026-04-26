
# Runtime Tests – Nikolai 0.3

import json
import os
import unittest

class TestRuntime(unittest.TestCase):

    def test_spine_exists(self):
        """
        The project spine must exist before runtime activation.
        """
        spine_path = 'C:/Nikolai_0_3/spine/project_spine.json'
        self.assertTrue(os.path.exists(spine_path))

    def test_spine_valid_json(self):
        """
        The project spine must contain valid JSON.
        """
        spine_path = 'C:/Nikolai_0_3/spine/project_spine.json'
        with open(spine_path, 'r') as f:
            try:
                json.load(f)
            except json.JSONDecodeError:
                self.fail("Project spine contains invalid JSON.")

    def test_identity_document_exists(self):
        """
        Identity must be defined before runtime activation.
        """
        identity_path = 'C:/Nikolai_0_3/brain/identity/Nikolai_0_3.md'
        self.assertTrue(os.path.exists(identity_path))

    def test_hands_module_exists(self):
        """
        Hands module must exist before runtime activation.
        """
        hands_path = 'C:/Nikolai_0_3/hands/processor.py'
        self.assertTrue(os.path.exists(hands_path))

    def test_runtime_files_exist(self):
        """
        Core runtime files must exist before activation.
        """
        required = [
            'C:/Nikolai_0_3/brain/runtime/core_runtime.py',
            'C:/Nikolai_0_3/brain/runtime/respond_loop.py',
            'C:/Nikolai_0_3/brain/runtime/context_manager.py'
        ]
        for path in required:
            self.assertTrue(os.path.exists(path))

if __name__ == '__main__':
    unittest.main()

if __name__ == '__main__':
    unittest.main()

