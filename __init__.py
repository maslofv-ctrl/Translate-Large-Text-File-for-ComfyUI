import os
from ollama import Client


class TranslateLargeFile:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_file": ("STRING", {"default": "novel_output.txt"}),
                "output_file": ("STRING", {"default": "novel_output_russian.txt"}),
                "chunk_size": ("INT", {
                    "default": 2000,
                    "min": 500,
                    "max": 8000,
                    "step": 100
                }),
                "system_prompt": ("STRING", {
                    "multiline": True,
                    "default": (
                        "Выступи в роли литературного переводчика, "
                        "виртуоза русского языка. Твоя задача — не просто "
                        "перевести слова, а создать на русском языке "
                        "полноценное художественное произведение, которое "
                        "сохранит душу, стиль и эстетическое воздействие "
                        "оригинала. Кроме перевода ничего добавлять не надо.\n\n"
                        "{text}"
                    )
                }),
            },
            "optional": {
                "connectivity": ("OLLAMA_CONNECTIVITY", {
                    "forceInput": True,
                    "tooltip": "Подключение Ollama Connectivity"
                }),
                "options": ("OLLAMA_OPTIONS", {
                    "forceInput": False,
                    "tooltip": "Ollama Options (temperature, top_p, etc.)"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_path",)
    FUNCTION = "translate"
    CATEGORY = "Text / Translation"

    def translate(
        self,
        input_file,
        output_file,
        chunk_size,
        system_prompt,
        connectivity,
        options=None,
    ):
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        url = connectivity["url"]
        model = connectivity["model"]

        keep_alive_unit = "m" if connectivity["keep_alive_unit"] == "minutes" else "h"
        keep_alive = str(connectivity["keep_alive"]) + keep_alive_unit

        client = Client(host=url)

        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = [
            text[i:i + chunk_size]
            for i in range(0, len(text), chunk_size)
        ]

        with open(output_file, "w", encoding="utf-8") as out_f:
            for i, chunk in enumerate(chunks, 1):
                print(f"Перевод части {i}/{len(chunks)}...")

                prompt = system_prompt.replace("{text}", chunk)

                response = client.generate(
                    model=model,
                    prompt=prompt,
                    options=self._filter_options(options),
                    keep_alive=keep_alive,
                )

                out_f.write(response["response"] + "\n")

        print(f"✅ Перевод сохранен в {output_file}")
        return (output_file,)

    def _filter_options(self, options):
        """
        Совместимо с OllamaOptionsV2
        """
        if not options:
            return None

        enabled = {}
        for k, v in options.items():
            if k.startswith("enable_") and v is True:
                key = k.replace("enable_", "")
                enabled[key] = options[key]

        return enabled or None


NODE_CLASS_MAPPINGS = {
    "TranslateLargeFile": TranslateLargeFile
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TranslateLargeFile": "Translate Large Text File (Ollama Connectivity)"
}
