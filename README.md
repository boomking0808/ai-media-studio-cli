# 🎨 AI MEDIA STUDIO CLI

<div align="center">

![AI Media Studio CLI](https://img.shields.io/badge/AI%20MEDIA-Studio%20CLI-FF6B6B?style=for-the-badge&logo=palette&logoColor=white)

### 🚀 Professional Multi-Modal AI Media Generation Tool
*Generate videos, images, and music with Google's AI models using simple text prompts*

[![Version](https://img.shields.io/badge/version-2.0.0-4ECDC4?style=for-the-badge)](https://github.com/Abdulrahman-Elsmmany/ai-media-studio-cli)
[![Python](https://img.shields.io/badge/python-3.13+-45B7D1?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-96CEB4?style=for-the-badge)](LICENSE)
[![Developer](https://img.shields.io/badge/Developer-Abdulrahman%20Elsmmany-FF6B6B?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Abdulrahman-Elsmmany)

![Multi-Modal](https://img.shields.io/badge/🎬-Video%20AI-FFA07A?style=for-the-badge)
![Images](https://img.shields.io/badge/🖼️-Image%20AI-9370DB?style=for-the-badge)
![Music](https://img.shields.io/badge/🎵-Music%20AI-FFD700?style=for-the-badge)
![Professional](https://img.shields.io/badge/⭐-Professional%20Grade-32CD32?style=for-the-badge)

</div>

---

## 🖼️ Experience AI Media Studio CLI

<div align="center">
  
### ✨ **Beautiful Terminal Interface for AI Media Generation**

![AI Media Studio CLI Interface](https://raw.githubusercontent.com/Abdulrahman-Elsmmany/Abdulrahman-Elsmmany/6a82e88919a47c45b5b7dd095a0a854bb4995054/assets/ai-media-studio-cli.png)

*🎬 Professional Multi-Modal AI Media Generation Tool with an intuitive terminal interface*

</div>

### 🎯 **Launch Interactive Mode**

```bash
# Start the beautiful interactive experience
ai-studio interactive
```

**Interactive Features:**
- 🎨 **Smart Media Selection** - Choose between Video, Image, or Music generation
- 🤖 **AI Model Showcase** - Compare capabilities of different models
- 📐 **Visual Parameter Config** - Real-time validation and previews
- 💡 **Prompt Writing Guide** - Built-in tips for each media type
- 📊 **Generation Preview** - See what you're about to create
- 🎯 **Intelligent Recommendations** - AI-powered suggestions
- 📁 **Automatic Organization** - Smart file management by media type

---

## 🎯 Why AI Media Studio CLI?

### ✨ **One Tool, All Media Types**
- 🎬 **Video Generation** with Google's latest Veo models
- 🖼️ **Image Creation** with Imagen (coming soon)
- 🎵 **Music Composition** with MusicLM (planned)
- 🎭 **Beautiful Interactive Mode** for easy media generation
- 📁 **Smart Organization** - Auto-sorts all your generated media

### 🚀 **Built for Creators**
- ⚡ **Fast Generation** - Optimized for quick results
- 🎨 **Professional Quality** - Using Google's best AI models
- 💻 **Developer Friendly** - Clean CLI with intuitive commands
- 🔄 **Extensible** - Easy to add new models and features

---

## 🚀 Quick Start Guide

### 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Abdulrahman-Elsmmany/ai-media-studio-cli.git
cd ai-media-studio-cli

# Install dependencies with UV (recommended)
uv sync

# Alternative: Install with pip
pip install -e .
```

### ⚙️ Configuration

Create your `.env` file with Google AI credentials:

```env
# 🔑 Google AI API Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_API_KEY=your-google-api-key

# 🪣 Google Cloud Storage Configuration
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket-name
GOOGLE_CLOUD_STORAGE_PATH=videos
```

### 🎯 Get Started in 30 Seconds

```bash
# 🎬 Generate your first video
ai-studio generate video -p "a cinematic sunset over mountains"

# 🎭 Or use interactive mode (recommended)
ai-studio interactive
```

---

## ✨ Multi-Modal AI Capabilities

<table>
<tr>
<td>

### 🎬 **Advanced Video Generation**
- **Google Veo 2.0 & 3.0** models
- **5-8 second** high-quality videos
- **Video extension** and continuation
- **Multiple aspect ratios** for all platforms

</td>
<td>

### 🖼️ **Professional Image Creation**
- **Google Imagen** models (coming soon)
- **Multiple resolutions** up to 4K
- **Style control** and customization
- **Batch generation** for workflows

</td>
</tr>
<tr>
<td>

### 🎵 **AI Music Composition**
- **Google MusicLM** integration (planned)
- **Custom length** and style control
- **Genre-specific** generation
- **High-quality audio** output

</td>
<td>

### 🖥️ **Premium User Experience**
- **Unified CLI interface** for all media types
- **Interactive mode** with beautiful UI
- **Real-time progress** tracking
- **Smart file organization** and downloads
- **Automatic media organization** (videos/, images/, audios/)
- **Concurrent downloads** with progress tracking

</td>
</tr>
</table>

---

## 🎯 Usage Examples

### 🎬 **Quick Video Generation**

```bash
# Simple video generation
ai-studio generate video -p "a majestic eagle soaring over mountains"

# With specific model and settings
ai-studio generate video \
  --prompt "cinematic drone shot of ocean waves at sunset" \
  --model veo3-001 \
  --aspect-ratio 16:9
```

### 📁 **Automatic Media Organization**

```bash
# All generated media is auto-organized:
downloaded_media/
├── videos/    # .mp4, .avi, .mov files
├── images/    # .jpg, .png, .gif files  
├── audios/    # .mp3, .wav, .flac files
└── unknown/   # Other file types
```

---

## 🎯 Advanced Examples

### 🎬 **Professional Video Generation**

```bash
# 🌅 Cinematic landscape video
ai-studio generate video \
  --prompt "golden hour cinematic shot of a serene lake with mountains reflected in still water" \
  --model veo3-001 \
  --aspect-ratio 16:9 \
  --resolution 1080 \
  --videos 2 \
  --duration 8

# 📱 Social media vertical video
ai-studio generate video \
  --prompt "trendy coffee shop aesthetic with latte art being created" \
  --model veo2-001 \
  --aspect-ratio 9:16 \
  --resolution 720 \
  --duration 6
```

### ➕ **Video Extension Workflows**

```bash
# 🔗 Extend video from Google Cloud Storage
ai-studio generate video \
  --prompt "the butterfly gracefully lands on a blooming flower petal" \
  --model veo2-001 \
  --extend-video "gs://your-bucket/nature-scene.mp4"

# 📁 Extend local video file
ai-studio generate video \
  --prompt "the sunset transforms into a starry night sky" \
  --model veo2-001 \
  --extend-video "./videos/sunset-base.mp4"
```

### 🖼️ **Image Generation** *(Coming Soon)*

```bash
# 🎨 High-resolution artwork
ai-studio generate image \
  --prompt "abstract digital art with vibrant colors and geometric patterns" \
  --model imagen-3-ultra \
  --resolution 2048x2048 \
  --style artistic

# 🏢 Professional photography
ai-studio generate image \
  --prompt "modern office interior with natural lighting" \
  --model imagen-3-001 \
  --resolution 1920x1080 \
  --style photorealistic
```

---

## 🤖 AI Model Ecosystem

<div align="center">

### 🎬 **Video Models**
| Model            | 🎯 Best For              | Videos | Duration | 🚀 Special Features                  |
| ---------------- | ----------------------- | ------ | -------- | ----------------------------------- |
| **veo2-001**     | 🎨 Creative & Flexible   | 4      | 5-8s     | ➕ Video Extension, 🖼️ Image-to-Video |
| **veo3-001**     | 🎬 Professional & Stable | 4      | 8s       | ✨ AI Prompt Enhancement             |
| **veo3-preview** | 🔬 Latest Features       | 4      | 8s       | 🖼️ Image-to-Video, 🆕 Beta Features   |

### 🖼️ **Image Models** *(Coming Soon)*
| Model              | 🎯 Best For           | Images | Resolution | 🚀 Special Features                   |
| ------------------ | -------------------- | ------ | ---------- | ------------------------------------ |
| **imagen-3-ultra** | 🎨 Ultra High Quality | 12     | Up to 4K   | 🎨 Style Control, ⚡ Fast Generation   |
| **imagen-3-001**   | 📸 Photorealistic     | 8      | Up to 2K   | 📷 Photo-realistic, 🎭 Face Generation |

### 🎵 **Music Models** *(Planned)*
| Model          | 🎯 Best For    | Length  | Quality | 🚀 Special Features                     |
| -------------- | ------------- | ------- | ------- | -------------------------------------- |
| **musiclm-v2** | 🎼 Composition | 30-120s | Hi-Fi   | 🎹 Instrument Control, 🎵 Genre Specific |

</div>

---

## 🎨 Creative Prompt Engineering

### 📝 **Universal Prompt Structure**

```
[STYLE] + [SUBJECT] + [ACTION] + [SETTING] + [TECHNICAL] + [MOOD]
```

### ✅ **Professional Examples by Media Type**

#### 🎬 **Video Prompts**
```bash
# Cinematic
"Cinematic wide shot of a lone figure walking through misty forest path, golden morning light filtering through ancient trees, slow dolly forward, mysterious atmosphere"

# Documentary
"Documentary-style close-up of artisan hands crafting pottery on spinning wheel, natural lighting, steady camera, focused concentration"
```

#### 🖼️ **Image Prompts** *(Coming Soon)*
```bash
# Artistic
"Abstract expressionist painting with bold brushstrokes, vibrant blues and oranges, dynamic composition, oil on canvas texture"

# Photographic
"Professional headshot of businesswoman in modern office, soft natural lighting, shallow depth of field, confident expression"
```

#### 🎵 **Music Prompts** *(Planned)*
```bash
# Instrumental
"Uplifting piano melody with string accompaniment, major key, 120 BPM, inspiring and motivational mood"

# Ambient
"Ethereal ambient soundscape with nature sounds, gentle synthesizer pads, relaxing meditation music"
```

### ❌ **Avoid These Mistakes**

```bash
❌ "make video"                   # Too vague, no media type specified
❌ "cool image of stuff"          # Lacks specific details
❌ "amazing epic best music"      # Over-hyped without substance
```

---


## 🛠️ Professional Development

### 📁 **Extensible Architecture**

```
ai-media-studio-cli/
├── 🎬 ai_media_studio_cli/
│   ├── main.py              # Unified CLI application
│   ├── ui_components.py     # Beautiful UI components
│   ├── models_config.py     # Multi-modal AI configurations
│   ├── model_manager.py     # Dynamic model handling
│   ├── download.py          # Smart media download & organization
│   ├── animations.py        # Progress & loading animations
│   ├── generators/
│   │   ├── video.py         # Video generation logic
│   │   ├── image.py         # Image generation (coming soon)
│   │   └── music.py         # Music generation (planned)
├── 📚 docs/
│   ├── ADDING_NEW_MODELS.md # Developer guide
│   ├── VIDEO_GENERATION.md  # Video-specific docs
│   └── ROADMAP.md           # Future feature roadmap
├── 🧪 tests/                # Comprehensive test suite
│   ├── test_download.py     # Download functionality tests
│   └── test_models.py       # Model integration tests
├── ⚙️ pyproject.toml        # Modern Python packaging
└── 📖 README.md             # This documentation
```

### 🚀 **Performance & Scalability**

- **Modular architecture** for easy extension to new AI models
- **Async processing** for all media types and downloads
- **Smart caching** to reduce API costs
- **Batch processing** for efficient generation workflows
- **Memory optimization** for large media files
- **Plugin system** for third-party model integration
- **Concurrent downloads** with progress tracking
- **Automatic file organization** by media type
- **GCS cleanup** to minimize storage costs

---

## 🗺️ Roadmap & Future Features

### 🎯 **Phase 1: Video Foundation** ✅
- ✅ Google Veo 2.0 & 3.0 integration
- ✅ Video extension capabilities
- ✅ Professional CLI interface
- ✅ Smart media download & organization
- ✅ Automatic folder structure (videos/, images/, audios/)
- ✅ Concurrent downloads with progress tracking

### 🎯 **Phase 2: Image Generation** 🚧
- 🔄 Google Imagen integration
- 🔄 Multiple resolution support
- 🔄 Style control and customization
- 🔄 Batch image processing

### 🎯 **Phase 3: Music Composition** 📋
- 📋 Google MusicLM integration
- 📋 Genre and style control
- 📋 Custom length generation
- 📋 Audio format optimization

### 🎯 **Phase 4: Advanced Features** 📋
- 📋 Multi-modal workflows (video + music)
- 📋 Template system for common use cases
- 📋 Cloud storage integration (AWS, Azure)
- 📋 API rate limiting and optimization
- 📋 Advanced prompt engineering tools

---

## 🎯 Advanced Configuration

### 🔧 **Environment Variables**

```env
# 🔑 Required - Google AI Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_API_KEY=your-google-api-key

# 🪣 Required - Google Cloud Storage
GOOGLE_CLOUD_STORAGE_BUCKET=your-bucket-name
GOOGLE_CLOUD_STORAGE_PATH=videos
```

### 🔑 **Google AI API Setup**

1. **Get your Google AI API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key for your project
   - Add it to your `.env` file as `GOOGLE_API_KEY`

2. **Configure Google Cloud Project**:
   - `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
   - `GOOGLE_CLOUD_LOCATION`: Recommended: `us-central1`
   - `GOOGLE_GENAI_USE_VERTEXAI`: Set to `True` for production use

### 🪣 **Google Cloud Storage Setup**

The tool requires a GCS bucket for temporary video storage during generation:

1. **Create a GCS bucket** in your Google Cloud project
2. **Set environment variables**:
   - `GOOGLE_CLOUD_STORAGE_BUCKET`: Your bucket name (e.g., `my-ai-videos`)
   - `GOOGLE_CLOUD_STORAGE_PATH`: Path within bucket (optional, defaults to `videos`)
3. **Ensure permissions**: Your service account needs `Storage Object Admin` role

### 📊 **Intelligent Media Management**

Generated content is automatically:
- 📁 **Organized by media type** (videos/, images/, audios/)
- 🏷️ **Tagged with generation metadata**
- 🧹 **Cleaned up** from cloud storage (optional)
- 📈 **Tracked** with detailed analytics
- 🔄 **Versioned** for iterative workflows
- ⚡ **Downloaded concurrently** with progress tracking
- 🎯 **Sorted by file extension** into appropriate folders
- 📦 **Supports 20+ media formats** (MP4, JPG, MP3, etc.)

---

## 📁 Smart Media Download & Organization

The CLI features an intelligent download system that automatically organizes your generated content:

### 🎯 **Automatic Organization**

```bash
# Downloads are automatically organized by media type
downloaded_media/
├── videos/     # .mp4, .avi, .mov, .mkv, .wmv, .flv, .webm, .m4v, .3gp
├── images/     # .jpg, .jpeg, .png, .gif, .bmp, .tiff, .svg, .webp, .ico
├── audios/     # .mp3, .wav, .flac, .aac, .ogg, .wma, .m4a, .opus
└── unknown/    # Unrecognized file types
```

### ⚡ **Performance Features**

- **Concurrent Downloads**: Multiple files downloaded simultaneously
- **Progress Tracking**: Real-time progress bars with ETA
- **Resume Support**: Automatic retry on network interruptions
- **GCS Cleanup**: Optional cloud storage cleanup after download
- **Memory Efficient**: Streaming downloads for large files

### 🔧 **Customization Options**

```bash
# Disable automatic organization
ai-studio generate video --no-organize

# Custom download directory
ai-studio generate video --output-dir "my-custom-folder"

# Keep files in cloud storage (no cleanup)
ai-studio generate video --keep-cloud-files
```

---

## 🤝 Contributing to the Future

We welcome contributions that push the boundaries of AI media generation:

### 🎯 **Contribution Areas**

1. 🎬 **Video Generation**: New models, effects, transitions
2. 🖼️ **Image Creation**: Style transfer, artistic filters
3. 🎵 **Music Composition**: Instrument separation, rhythm generation
4. 🖥️ **User Experience**: Interface improvements, workflow optimization
5. 🔧 **Technical**: Performance, architecture, new integrations

### 🏆 **Code Standards**

- **Type hints** for all functions across all modules
- **Comprehensive docstrings** with examples
- **Unit tests** with >95% coverage for new features
- **Integration tests** for AI model endpoints
- **Performance benchmarks** for generation workflows

---

## 📞 Support & Community

<div align="center">

### 🌟 **Get Help & Connect**

[![Issues](https://img.shields.io/badge/🐛-Report%20Issues-FF6B6B?style=for-the-badge)](https://github.com/Abdulrahman-Elsmmany/ai-media-studio-cli/issues)
[![Discussions](https://img.shields.io/badge/💬-Join%20Discussion-4ECDC4?style=for-the-badge)](https://github.com/Abdulrahman-Elsmmany/ai-media-studio-cli/discussions)
[![Documentation](https://img.shields.io/badge/📖-Documentation-45B7D1?style=for-the-badge)](https://github.com/Abdulrahman-Elsmmany/ai-media-studio-cli/wiki)

### 🎨 **Media Showcase**
Share your AI-generated content with the community!
[![Gallery](https://img.shields.io/badge/🖼️-Community%20Gallery-FF69B4?style=for-the-badge)](https://github.com/Abdulrahman-Elsmmany/ai-media-studio-cli/discussions/categories/showcase)

</div>

---

## 📄 License & Attribution

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for complete details.

**Third-party acknowledgments:**
- 🤖 **Google AI** for Veo, Imagen, and MusicLM model access
- 🎨 **Rich** for beautiful terminal UI
- ⚡ **Typer** for modern CLI framework
- 🔧 **UV** for fast Python package management

---

<div align="center">

### 🎨 **AI MEDIA STUDIO CLI**

*The future of AI media generation in your terminal*

**Created with ❤️ by [Abdulrahman Elsmmany](https://github.com/Abdulrahman-Elsmmany)**

[![GitHub](https://img.shields.io/badge/GitHub-Abdulrahman-Elsmmany-181717?style=for-the-badge&logo=github)](https://github.com/Abdulrahman-Elsmmany)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/abdulrahman-elsmmany)

---

**⭐ Star this repository if it helped you create amazing AI content!**

*Let's build the future of AI media generation together* 🚀

### 🎬🖼️🎵 *Videos • Images • Music - All Powered by AI*

</div>