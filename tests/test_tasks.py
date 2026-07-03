from admitflow_ai.cli import sample_tasks


def test_sample_tasks_include_deadlines() -> None:
    assert all(task.due for task in sample_tasks())

