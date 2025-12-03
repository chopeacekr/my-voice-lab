# 🎙️ My Voice Lab

> **他の言語で読む**: [English](./README.md) | [한국어](./README.ko.md)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29%2B-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.3.0-orange)](CHANGELOG.md)

> **高度なオーディオ分析機能を備えたマルチTTS/STT統合システム**

**5つのTTSモデル**と**4つのSTTモデル**を統合したPeace Chatbotシステム。オーディオ可視化および分析機能を含む。

![デモスクリーンショット](./images/experimental_mode.png)

---

## ✨ 主な機能

- 🎤 **マルチSTTサポート** - Google SR、Whisper、Wav2Vec2、Vosk
- 🔊 **マルチTTSサポート** - gTTS、MeloTTS、XTTS v2、F5-TTS、Bark
- 🌍 **13言語対応** - 韓国語、英語、日本語、中国語、フランス語など
- 🎨 **ボイスクローニング** - XTTS v2 & F5-TTS ゼロショットボイスクローニング
- 🧪 **実験モード** - Waveform/Spectrogramビジュアライゼーション + ZIPエクスポート
- 🤖 **Gemini LLM統合** - Google Geminiとの自然な会話
- ⚡ **サーバー不要** - gTTS + Google SRで即座に開始（インターネットのみ必要）
- 🏗️ **マイクロサービスアーキテクチャ** - 9つの独立したリポジトリ

---

## 🚀 クイックスタート

### 前提条件

- Python 3.11+
- インターネット接続（gTTS & Google SR用）

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/chopeacekr/my-voice-lab.git
cd my-voice-lab

# uvをインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係をインストール
uv sync

# 実行！
uv run streamlit run web.py
```

ブラウザを開く: **http://localhost:8501**

**完了！** 🎉 サーバー設定は不要です。

---

## 📊 モデル比較

### TTSモデル

| モデル | 速度 | 品質 | サーバー | ボイスクローニング | 推奨用途 |
|--------|------|------|----------|-------------------|----------|
| **gTTS** | ⚡⚡⚡ 0.5秒 | ⭐⭐⭐ | 不要 | ❌ | クイックスタート |
| **MeloTTS** | ⚡⚡ 1-2秒 | ⭐⭐⭐⭐ | 必要 | ❌ | リアルタイム |
| **XTTS v2** | ⚡ 5-10秒 | ⭐⭐⭐⭐⭐ | 必要 | ✅ | ボイスクローニング |
| **F5-TTS** | 10-20秒 | ⭐⭐⭐⭐⭐ | 必要 | ✅ | 最高品質 |
| **Bark** | 100-200秒 | ⭐⭐⭐⭐⭐ | 必要 | ❌ | 感情/音楽 |

### STTモデル

| モデル | 速度 | 精度 | サーバー | オフライン | 推奨用途 |
|--------|------|------|----------|-----------|----------|
| **Google SR** | ⚡⚡⚡ 0.8秒 | 85% | 不要 | ❌ | クイックスタート |
| **Whisper** | ⚡⚡ 1.3秒 | 90% | 必要 | ✅ | 最高精度 |
| **Wav2Vec2** | ⚡⚡ 1.5秒 | 82% | 必要 | ✅ | 韓国語最適化 |
| **Vosk** | ⚡⚡⚡ 0.9秒 | 78% | 必要 | ✅ | 軽量 |

---

## 🎮 使い方

### 基本的な使用法（サーバー不要）

1. アプリを起動: `uv run streamlit run web.py`
2. サイドバーで**GEMINI API Key**を入力
3. **gTTS**（TTS）と**Google SR**（STT）を選択
4. 🎤をクリックして録音 → 話す → 停止
5. **Send**をクリック → 音声でAI応答を受け取る！

### ボイスクローニング（XTTS v2）

1. TTS Modelで**XTTS v2**を選択
2. "Record your voice sample"で🎤をクリック
3. 自分の声を3-5秒録音
4. メッセージを入力して**Send**をクリック
5. **自分の声で**AI応答！🎉

### 実験モード

1. **🧪 Experimental Mode**をON
2. 音声録音 → 自動STT認識
3. オーディオプレーヤー付きチャットメッセージ保存
4. **💾 保存 & グラフ表示**をクリック
5. ZIPファイルをダウンロード:
   - オリジナルオーディオ（WAV）
   - Waveform（PNG）
   - Spectrogram（PNG）

---

## 📚 ドキュメント

- **[REPORT.md](./REPORT.md)** - 詳細な実装レポート（韓国語）
- **[CHANGELOG.md](./CHANGELOG.md)** - バージョン履歴
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** - 貢献ガイド

---

## 📄 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - [LICENSE](LICENSE)ファイルを参照してください。

---

## 📞 連絡先

**Peace Cho**

- GitHub: [@chopeacekr](https://github.com/chopeacekr)
- Email: chopeacekr@gmail.com
- プロジェクト: [https://github.com/chopeacekr/my-voice-lab](https://github.com/chopeacekr/my-voice-lab)

---

<div align="center">

**Made with ❤️ by Peace Cho**

[⬆ トップに戻る](#-my-voice-lab)

</div>