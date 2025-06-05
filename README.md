# EmoteCraft: Affect-Responsive Dialogue System for Game Characters

## 🚀 What's New in EmoteCraft?
- **AI-Driven Emotional Portraits**: Automatically generate character portraits that reflect the emotion in dialogue.
- **Modern Web Interface**: User-friendly, responsive UI for dialogue browsing and portrait generation.
- **Model Selection**: Choose from multiple AI models (pixel, cartoon, realistic, etc.) for different art styles.
- **Prompt Caching**: LLM-generated prompts are cached for efficiency and speed.
- **No Image Caching**: Every generation is unique, even with the same parameters.

---

## 📖 Introduction
![99dd92821a47fa526faf9a869093f28](https://github.com/user-attachments/assets/4488b6ca-d984-4dd3-8780-748e9aab9721)
This project proposes the development of an **Affect-Responsive Dialogue System** for game characters, inspired by the relationship between dialogue, emotional state, and character portrayal as seen in the provided example. The system aims to enable NPCs to dynamically alter their dialogue—and optionally facial expressions or behavior—based on an analyzed emotional state. This creates more immersive and believable interactions.

> **Example Reference**: A character resembling Emily from *Stardew Valley* says,  
> *"你让我心都碎了……我不能再和你说话了。"*  
> *(“you've broken my heart...I can't talk to you anymore.”)*  
>  
> **Mood Analysis**: The dialogue conveys strong negative emotion, reflecting emotional pain and disappointment. Terms like "心都碎了" ("heartbroken") express sadness and betrayal, while the refusal to continue the conversation suggests a state of anger, despair, and emotional withdrawal.


---

## 🖥️ Web Interface & Usage
- **Main Page**: 
  - Prominently displays the EmoteCraft name and a brief introduction.
  - Allows users to select a dialogue group and open the dialogue interface.
  - Beautiful Stardew Valley-inspired background.
- **Dialogue Page**:
  - Shows character portrait, dialogue, and navigation.
  - Right panel for model/denoise selection and real-time prompt display.
  - "Back to Home" button for easy navigation.

### How to Run
1. **Install dependencies**:
   ```bash
   pip install flask requests
   ```
2. **Prepare your data**:
   - Place dialogue JSON files in `Data/dialogue/Chinese/`.
   - Place character avatars in `input3/`.
   - Place your background image in `static/images/stardew_bg.png`.
3. **Start ComfyUI**:
   - Make sure you have a [ComfyUI](https://github.com/comfyanonymous/ComfyUI) environment running at `127.0.0.1:8188` (default port) for image generation to work.
4. **Run the app**:
   ```bash
   python app.py
   ```
5. **Open your browser** and visit `http://localhost:5000`.

---

## ⚙️ LLM API Configuration
To enable AI prompt generation, you need to configure your LLM (Large Language Model) API credentials. Set the following environment variables before running the app:

- `LLM_API_BASE` — The base URL of your LLM API (e.g., OpenAI-compatible endpoint)
- `LLM_API_KEY` — Your API key/token
- `LLM_MODEL_NAME` — The model name to use (e.g., `gpt-3.5-turbo`, `deepseek-chat`)

**Example (Linux/macOS):**
```bash
export LLM_API_BASE="https://api.openai.com/v1"
export LLM_API_KEY="sk-xxxxxxx"
export LLM_MODEL_NAME="gpt-3.5-turbo"
```

**Example (Windows CMD):**
```cmd
set LLM_API_BASE=https://api.openai.com/v1
set LLM_API_KEY=sk-xxxxxxx
set LLM_MODEL_NAME=gpt-3.5-turbo
```
---

## 📜 License

This project is licensed under the **MIT License**.

## 📬 Contact & Contribution

We welcome feedback, suggestions, and contributions!
-   **GitHub Repository Issues Page**: For bug reports, feature requests, and discussions, please submit on the [[Issues](https://github.com/ChrisMao0325/EmoteCraft/issues)]

