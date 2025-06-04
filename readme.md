# video_cutter

**A high-performance batch video processor built for marketplace-ready media.  
Author: Dmitry Kulagin**

---

## 📦 About

`video_cutter` is a production-grade desktop tool that prepares videos for marketplace upload by trimming, resizing, cropping, and standardizing raw footage from fashion shoots.

**Developed, deployed, and actively used by the company [Kari](https://kari.com)** — a leading fashion retailer — the solution handles thousands of videos in a matter of hours, replacing manual editing with fast, scalable automation.

---

## 🛠 Features

- Batch trimming: remove unnecessary intros or idle segments  
- Target duration enforcement (e.g. 20 seconds max)  
- Aspect-ratio-aware scaling and center-cropping  
- Audio removal (required by many platforms)  
- Handles video rotation metadata from phones/cameras  
- Supports `.mp4`, `.avi`, `.mov`, `.mkv`  
- GUI-based controls via `tkinter`  
- Full logging to file and console

---

## 🚀 Usage

```bash
python Video_cutter/video_cutter_v2_0.py
