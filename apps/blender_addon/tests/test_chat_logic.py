import importlib
import unittest


class TestChatLogic(unittest.TestCase):
    def setUp(self):
        self.logic = importlib.import_module(
            "apps.blender_addon.blender_ai_copilot.state.chat_logic"
        )

    def test_hello_generates_ready_mock_response(self):
        session = self.logic.default_session()
        session = self.logic.send_user_message(session, "Hello")

        self.assertEqual(session["ui_state"], "completed")
        self.assertTrue(any(m["role"] == "user" for m in session["messages"]))
        self.assertTrue(
            any(
                m["role"] == "assistant"
                and m["content"] == "Blender AI Copilot is ready."
                for m in session["messages"]
            )
        )

    def test_error_then_retry(self):
        session = self.logic.default_session()
        session = self.logic.send_user_message(session, "/error")

        self.assertEqual(session["ui_state"], "error")
        self.assertTrue(session["can_retry"])

        session = self.logic.retry_last(session)
        self.assertEqual(session["ui_state"], "completed")
        self.assertFalse(session["can_retry"])

    def test_cancel_and_clear(self):
        session = self.logic.default_session()
        session = self.logic.send_user_message(session, "Move something")
        session = self.logic.cancel_current(session)

        self.assertEqual(session["ui_state"], "cancelled")

        cleared = self.logic.clear_conversation(session)
        self.assertEqual(cleared["ui_state"], "idle")
        self.assertEqual(cleared["messages"], [])

    def test_backend_completion_records_agent_tool_activity(self):
        session = self.logic.default_session()
        completed = self.logic.complete_backend_turn(
            session,
            "There are 3 objects.",
            tool_calls=[{"name": "get_scene_summary"}],
        )

        self.assertEqual(
            completed["tool_activity"]["label"], "Completed: get_scene_summary"
        )

    def test_agent_proposal_waits_for_approval_without_execution(self):
        session = self.logic.default_session()
        proposed = self.logic.await_agent_proposal(
            session,
            "Prepared a transform proposal.",
            {
                "id": "proposal-1",
                "sceneName": "Demo",
                "targets": [{"id": "tree-1", "name": "Tree Oak"}],
                "locationDelta": [-2, 0, 0],
                "rotationDelta": [0, 0, 0],
                "scaleMultiplier": [1, 1, 1],
            },
        )

        self.assertEqual(proposed["ui_state"], "awaiting_approval")
        self.assertEqual(proposed["proposal"]["source"], "agent")

        previewed = self.logic.preview_agent_proposal(
            proposed, {"proposal_id": "proposal-1", "targets": [], "count": 0}
        )
        self.assertEqual(previewed["ui_state"], "proposal")

        executed = self.logic.complete_agent_execution(
            previewed, {"proposal_id": "proposal-1", "count": 1}
        )
        self.assertTrue(executed["undo_available"])
        self.assertEqual(executed["ui_state"], "completed")

        undone = self.logic.record_undo(executed)
        self.assertFalse(undone["undo_available"])

    def test_proposal_lifecycle(self):
        session = self.logic.default_session()
        session = self.logic.seed_mock_proposal(session)
        self.assertEqual(session["ui_state"], "awaiting_approval")
        self.assertIsNotNone(session["proposal"])

        previewed = self.logic.preview_proposal(session)
        self.assertEqual(previewed["ui_state"], "proposal")

        applied = self.logic.apply_proposal(session)
        self.assertEqual(applied["ui_state"], "completed")
        self.assertIsNone(applied["proposal"])


if __name__ == "__main__":
    unittest.main()
