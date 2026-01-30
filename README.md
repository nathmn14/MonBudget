# 💰 MonBudget - Smart Personal Finance Manager

**MonBudget** is a modern, cross-platform personal finance management application built with Python. It empowers users to track their expenses and income with ease, featuring a sophisticated **Smart Voice Command** system that makes financial logging as simple as speaking.

---

## 🚀 Key Features

- 📊 **Dynamic Dashboard**: Visualize your financial health with real-time charts and statistics.
- 📥 **Transaction Management**: Categorize and track every cent with ease.
- 🏷️ **Intelligent Categorization**: Manage custom categories with unique icons and colors.
- 📅 **Budget Planning**: Set monthly limits and monitor your progress.
- 🔐 **Secure Access**: Integrated user authentication and database protection.
- 💳 **Multi-Account Support**: Manage multiple wallets and bank accounts in one place.
- 📱 **Cross-Platform**: Runs seamlessly on **Android**, **Windows**, and **Linux**.
- 🌐 **Multilingual Support**: Optimized for French and English.

---

## 🎙️ The Highlight: Smart Voice Commands

The most powerful feature of MonBudget is the **Integrated Voice Assistant**. Designed to feel like Google Assistant, it allows you to add transactions naturally without touching a single button.

### How it Works:
1. **Natural Language Processing (NLP)**: The engine parses your speech to extract the **amount**, the **transaction type** (income/expense), and the **category**.
2. **Contextual Awareness**: If you say *"Spent 5000 for Restaurant"*, the app automatically:
   - Identifies the amount (5000).
   - Identifies the type (Expense).
   - Searches for a "Restaurant" category.
3. **Auto-Learning**: If a category mentioned doesn't exist, MonBudget intelligently creates it for you, assigning a relevant icon based on keywords (e.g., "Food", "Medical", "Home").
4. **Interactive UI**: A sleek, pulsing microphone interface provides real-time feedback (Listening -> Processing -> Success/Error).
5. **Vocal Feedback (TTS)**: The app confirms the transaction audibly, providing a truly hands-free experience.

### Technical Implementation:
- **Android**: Leverages `RecognizerIntent` for high-accuracy native speech recognition.
- **Desktop**: Uses the `SpeechRecognition` library with the Google Web Speech API.
- **Cross-Platform Audio**: `pyttsx3` and `Plyer` handle text-to-speech feedback across all devices.

---

## 🛠️ Technology Stack

- **Core**: Python 3
- **UI Framework**: Kivy & KivyMD (Material Design)
- **Database**: SQLite3
- **Automation**: Buildozer (for Android packaging)
- **Voice Engine**: 
  - `SpeechRecognition` (STT)
  - `pyttsx3` / `plyer` (TTS)
  - `jnius` (Android Bridge)

---

## 📂 Project Architecture

The project follows a clean **MVC (Model-View-Controller)** pattern:

- **`models/`**: Handles database interactions and data structures.
- **`views/`**: Contains `.kv` files defining the Material Design interface.
- **`controllers/`**: Manages the application logic and bridges the Models and Views.
- **`utils/`**: Core utilities, including the `voice_engine.py` and `voice_transaction.py` logic.

---

## 📥 Installation

### Prerequisites
- Python 3.8+
- [Kivy dependencies](https://kivy.org/doc/stable/installation/installation-windows.html)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/MonBudget.git
   cd MonBudget
   ```

2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

---

## 💡 Usage Tips

- **Voice Command**: Long-press the microphone icon on the dashboard or transaction screen.
- **Examples to try**:
  - *"J'ai dépensé 10000 francs pour le loyer"* (I spent 10,000 francs for rent)
  - *"Salaire reçu de 500 dollars"* (Salary received 500 dollars)
  - *"Dépense 5000 restaurant"* (Expense 5000 restaurant)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Created with ❤️ by nathmn14*
