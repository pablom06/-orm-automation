#!/usr/bin/env python3
"""
Video Generator — Pablo M. Rivera ORM
======================================
Generates a 90-120 second slideshow video from an article using:
  - PIL for slide images
  - edge-tts (free Microsoft TTS) for narration
  - moviepy for video assembly

Usage:
  python make_video.py --day 25
  python make_video.py --day 25 --output videos/custom.mp4
"""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
ARTICLES_FILE = BASE_DIR / "articles" / "articles.json"
VIDEOS_DIR = BASE_DIR / "videos"
TEMP_DIR = BASE_DIR / "videos" / "_temp"
VIDEOS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Brand colors
DARK_BLUE = (26, 26, 46)
GREEN = (52, 211, 153)
WHITE = (255, 255, 255)
LIGHT_GRAY = (240, 244, 248)

WIDTH, HEIGHT = 1920, 1080
VOICE = "en-US-AndrewNeural"  # Professional masculine voice


def load_articles():
    with open(ARTICLES_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_font(size, bold=False):
    """Get a font, falling back through common system locations."""
    from PIL import ImageFont
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current = []
    for word in words:
        test = " ".join(current + [word])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def draw_slide(title, body_text, slide_path, slide_type="content"):
    """Draw a slide as a 1920x1080 PNG."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (WIDTH, HEIGHT), DARK_BLUE)
    draw = ImageDraw.Draw(img)

    if slide_type == "title":
        # Brand bar at bottom
        draw.rectangle([0, HEIGHT - 30, WIDTH, HEIGHT], fill=GREEN)

        # "PABLO M. RIVERA" header
        header_font = get_font(48, bold=True)
        draw.text((100, 100), "PABLO M. RIVERA", fill=GREEN, font=header_font)

        # Title (large, centered vertically)
        title_font = get_font(80, bold=True)
        title_lines = wrap_text(title, title_font, WIDTH - 200, draw)
        y = 280
        for line in title_lines:
            draw.text((100, y), line, fill=WHITE, font=title_font)
            y += 100

        # Subtitle
        sub_font = get_font(40)
        draw.text((100, HEIGHT - 200), "Operations Executive | 25+ Years Experience",
                  fill=LIGHT_GRAY, font=sub_font)

    elif slide_type == "outro":
        draw.rectangle([0, HEIGHT - 30, WIDTH, HEIGHT], fill=GREEN)
        big_font = get_font(80, bold=True)
        link_font = get_font(56, bold=True)
        sub_font = get_font(40)

        draw.text((100, 250), "Connect with", fill=LIGHT_GRAY, font=sub_font)
        draw.text((100, 320), "Pablo M. Rivera", fill=WHITE, font=big_font)
        draw.text((100, 480), "pablomrivera.com", fill=GREEN, font=link_font)
        draw.text((100, 580), "linkedin.com/in/pablo-rivera-74861a234", fill=LIGHT_GRAY, font=sub_font)

    else:
        # Side accent bar
        draw.rectangle([0, 0, 20, HEIGHT], fill=GREEN)

        # Title
        title_font = get_font(64, bold=True)
        title_lines = wrap_text(title, title_font, WIDTH - 200, draw)
        y = 80
        for line in title_lines[:2]:
            draw.text((100, y), line, fill=WHITE, font=title_font)
            y += 80

        # Body bullets
        body_font = get_font(44)
        y = max(y + 60, 280)
        for line in body_text:
            wrapped = wrap_text(f"• {line}", body_font, WIDTH - 200, draw)
            for w_line in wrapped[:2]:  # max 2 lines per bullet
                if y > HEIGHT - 100:
                    break
                draw.text((100, y), w_line, fill=LIGHT_GRAY, font=body_font)
                y += 70
            y += 20

    img.save(slide_path)
    return slide_path


async def generate_tts(text, output_path):
    """Generate TTS audio file."""
    import edge_tts
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(str(output_path))


def get_audio_duration(path):
    """Get duration of an audio file."""
    from moviepy.editor import AudioFileClip
    clip = AudioFileClip(str(path))
    duration = clip.duration
    clip.close()
    return duration


def parse_article_sections(body):
    """Extract heading + content pairs from markdown body."""
    sections = []
    current_heading = None
    current_lines = []
    for line in body.split("\n"):
        h = re.match(r'^#{1,3}\s+(.+)$', line)
        if h:
            if current_heading and current_lines:
                sections.append((current_heading, " ".join(current_lines).strip()))
            current_heading = h.group(1).strip()
            current_lines = []
        elif line.strip() and not line.startswith("*By ") and not line.startswith("["):
            clean = re.sub(r'[*_`]', '', line.strip())
            clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean)
            if clean:
                current_lines.append(clean)
    if current_heading and current_lines:
        sections.append((current_heading, " ".join(current_lines).strip()))
    return sections


def build_video(article, output_path):
    """Build a slideshow video for an article."""
    from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

    title = article["title"]
    body = article["body"]
    day = article["day"]

    sections = parse_article_sections(body)
    work_dir = TEMP_DIR / f"day_{day:03d}"
    work_dir.mkdir(exist_ok=True, parents=True)

    # Build slide plans: (slide_type, title, body_lines, narration)
    slides = []

    # Slide 1: Title
    title_narration = (
        f"In this video, Pablo M. Rivera discusses {title}. "
        f"Pablo is an operations executive with over 25 years of experience leading teams "
        f"across construction, finance, technology, and property management."
    )
    slides.append(("title", title, [], title_narration))

    # Content slides (up to 3 sections)
    for heading, content in sections[:3]:
        first_sentence = content.split(". ")[0]
        if len(first_sentence) > 250:
            first_sentence = first_sentence[:250] + "..."

        # Pull short bullets for slide visual
        bullets = []
        for sentence in content.split(". ")[:3]:
            s = sentence.strip().rstrip(".")
            if 20 < len(s) < 120:
                bullets.append(s)
        if not bullets:
            bullets = [content[:120]]

        narration = f"{heading}. {first_sentence}."
        slides.append(("content", heading, bullets, narration))

    # Outro slide
    outro_narration = (
        "To learn more, visit pablomrivera.com or connect with Pablo on LinkedIn. "
        "Thank you for watching."
    )
    slides.append(("outro", "Connect", [], outro_narration))

    # Generate audio + images
    print(f"📹 Building video for Day {day}: {title[:60]}")
    clips = []
    for i, (slide_type, slide_title, body_lines, narration) in enumerate(slides):
        slide_img = work_dir / f"slide_{i:02d}.png"
        audio_file = work_dir / f"audio_{i:02d}.mp3"

        print(f"   Slide {i+1}/{len(slides)}: drawing image...")
        draw_slide(slide_title, body_lines, slide_img, slide_type=slide_type)

        print(f"   Slide {i+1}/{len(slides)}: generating TTS...")
        asyncio.run(generate_tts(narration, audio_file))

        duration = get_audio_duration(audio_file)
        print(f"   Slide {i+1}/{len(slides)}: duration={duration:.1f}s")

        img_clip = ImageClip(str(slide_img)).set_duration(duration)
        audio_clip = AudioFileClip(str(audio_file))
        video_clip = img_clip.set_audio(audio_clip)
        clips.append(video_clip)

    print("📹 Concatenating clips...")
    final = concatenate_videoclips(clips, method="compose")
    print(f"📹 Writing video to {output_path}...")
    final.write_videofile(
        str(output_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=2,
        preset="medium",
        logger=None,
    )

    # Cleanup clips
    for clip in clips:
        clip.close()
    final.close()

    print(f"✅ Video built: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int, required=True, help="Article day number")
    parser.add_argument("--output", type=str, help="Output path (default: videos/day_XXX_title.mp4)")
    args = parser.parse_args()

    articles = load_articles()
    article = next((a for a in articles if a["day"] == args.day), None)
    if not article:
        print(f"❌ No article found for day {args.day}")
        sys.exit(1)

    if args.output:
        out_path = Path(args.output)
    else:
        slug = re.sub(r'[^a-z0-9]+', '-', article["title"].lower()).strip('-')[:60]
        out_path = VIDEOS_DIR / f"day_{args.day:03d}_{slug}.mp4"

    out_path.parent.mkdir(exist_ok=True, parents=True)
    build_video(article, out_path)


if __name__ == "__main__":
    main()
