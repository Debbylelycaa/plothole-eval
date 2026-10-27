from types import SimpleNamespace

from plothole.inference.client import call_model


class FakeCompletions:
    def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            model="model-x-2026-10-01",
            choices=[SimpleNamespace(
                message=SimpleNamespace(content='{"plot_holes": []}'), finish_reason="stop")],
            usage=SimpleNamespace(prompt_tokens=1_000_000, completion_tokens=100_000,
                                  completion_tokens_details=None),
        )


def test_call_model_meneruskan_params_dan_menghitung_biaya():
    completions = FakeCompletions()
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    mcfg = {
        "model_id": "model-x",
        "price_per_mtok": {"input": 2.0, "output": 10.0},
        "params": {"reasoning_effort": "low", "max_tokens": 100},
    }
    out = call_model(client, mcfg, [{"role": "user", "content": "hai"}])

    assert completions.kwargs["reasoning_effort"] == "low"   # params diteruskan apa adanya
    assert completions.kwargs["model"] == "model-x"
    assert out["model_returned"] == "model-x-2026-10-01"
    assert out["cost_usd"] == 2.0 + 1.0                       # 1 jt x $2 + 100 rb x $10
    assert out["finish_reason"] == "stop"