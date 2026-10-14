#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use eframe::egui::{self, Align, Color32, Layout, RichText, ScrollArea, Stroke};
use image::{DynamicImage, ImageBuffer, Rgb};
use libheif_rs::{ColorSpace, HeifContext, LibHeif, RgbChroma};
use std::{collections::HashSet, fs, io::Write, path::{Path, PathBuf}, sync::mpsc::{self, Receiver}, thread};
use walkdir::WalkDir;

const MAX_FILES: usize = 20;
const APP_TITLE: &str = "HEIC to JPG Converter | TCDOVERLORD";

#[derive(Clone, Debug)]
struct Entry {
    path: PathBuf,
    status: String,
    detail: String,
}

#[derive(Debug)]
enum WorkerMsg {
    Progress(usize, String, String),
    Done,
}

struct ConverterApp {
    files: Vec<Entry>,
    output: String,
    quality: u8,
    busy: bool,
    status: String,
    completed: usize,
    failed: usize,
    receiver: Option<Receiver<WorkerMsg>>,
}

impl Default for ConverterApp {
    fn default() -> Self {
        Self {
            files: Vec::new(), output: String::new(), quality: 95, busy: false,
            status: "Drop up to 20 HEIC/HEIF photos here, or choose files below.".into(),
            completed: 0, failed: 0, receiver: None,
        }
    }
}

impl ConverterApp {
    fn add_paths(&mut self, paths: impl IntoIterator<Item = PathBuf>) {
        let mut seen: HashSet<PathBuf> = self.files.iter().map(|e| canonical_or_original(&e.path)).collect();
        let mut added = 0usize;
        let mut ignored = 0usize;
        for p in paths {
            if p.is_dir() {
                for item in WalkDir::new(&p).follow_links(false).into_iter().filter_map(Result::ok) {
                    if item.file_type().is_file() && is_heic(item.path()) {
                        if self.files.len() >= MAX_FILES { ignored += 1; continue; }
                        let path = item.path().to_path_buf();
                        if seen.insert(canonical_or_original(&path)) {
                            self.files.push(Entry { path, status: "Ready".into(), detail: String::new() }); added += 1;
                        }
                    }
                }
            } else if p.is_file() && is_heic(&p) {
                if self.files.len() >= MAX_FILES { ignored += 1; continue; }
                if seen.insert(canonical_or_original(&p)) {
                    self.files.push(Entry { path: p, status: "Ready".into(), detail: String::new() }); added += 1;
                }
            }
        }
        if self.output.is_empty() {
            if let Some(first) = self.files.first() {
                let parent = first.path.parent().unwrap_or_else(|| Path::new("."));
                self.output = parent.join("JPG Converted").to_string_lossy().into_owned();
            }
        }
        self.status = if ignored > 0 {
            format!("Added {added} file(s). The 20-file limit was reached; {ignored} additional match(es) were ignored.")
        } else { format!("{} of {MAX_FILES} files selected.", self.files.len()) };
    }

    fn choose_files(&mut self) {
        if let Some(paths) = rfd::FileDialog::new()
            .add_filter("HEIC / HEIF photos", &["heic", "heif", "HEIC", "HEIF"])
            .set_title("Select up to 20 HEIC/HEIF photos")
            .pick_files() { self.add_paths(paths); }
    }

    fn choose_folder(&mut self) {
        if let Some(path) = rfd::FileDialog::new().set_title("Choose a folder with HEIC/HEIF photos").pick_folder() {
            self.add_paths([path]);
        }
    }

    fn choose_output(&mut self) {
        if let Some(path) = rfd::FileDialog::new().set_title("Choose destination folder for JPGs").pick_folder() {
            self.output = path.to_string_lossy().into_owned();
        }
    }

    fn start(&mut self) {
        if self.files.is_empty() { self.status = "Add at least one HEIC/HEIF photo first.".into(); return; }
        let out = PathBuf::from(self.output.trim());
        if self.output.trim().is_empty() { self.status = "Choose a destination folder first.".into(); return; }
        if let Err(e) = fs::create_dir_all(&out) { self.status = format!("Cannot create destination folder: {e}"); return; }
        let jobs: Vec<PathBuf> = self.files.iter().map(|e| e.path.clone()).collect();
        let quality = self.quality;
        let (tx, rx) = mpsc::channel();
        self.receiver = Some(rx);
        self.busy = true; self.completed = 0; self.failed = 0;
        for e in &mut self.files { e.status = "Queued".into(); e.detail.clear(); }
        self.status = format!("Converting {} file(s)...", jobs.len());
        thread::spawn(move || {
            for (idx, source) in jobs.iter().enumerate() {
                let (state, detail) = match convert_one(source, &out, quality) {
                    Ok(target) => ("Done".to_string(), format!("Saved: {}", target.display())),
                    Err(err) => ("Failed".to_string(), format!("{}", err)),
                };
                if tx.send(WorkerMsg::Progress(idx, state, detail)).is_err() { return; }
            }
            let _ = tx.send(WorkerMsg::Done);
        });
    }

    fn poll_worker(&mut self) {
        let mut pending = Vec::new();
        if let Some(rx) = &self.receiver { while let Ok(msg) = rx.try_recv() { pending.push(msg); } }
        for msg in pending {
            match msg {
                WorkerMsg::Progress(idx, state, detail) => {
                    if let Some(item) = self.files.get_mut(idx) {
                        item.status = state.clone(); item.detail = detail;
                        if state == "Done" { self.completed += 1; } else { self.failed += 1; }
                    }
                    self.status = format!("Processed {}/{} Â· {} successful Â· {} failed", self.completed + self.failed, self.files.len(), self.completed, self.failed);
                }
                WorkerMsg::Done => {
                    self.busy = false;
                    self.status = format!("Finished: {} converted, {} failed. Original photos were not changed.", self.completed, self.failed);
                    self.receiver = None;
                }
            }
        }
    }
}

impl eframe::App for ConverterApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        self.poll_worker();
        let dropped = ctx.input(|i| i.raw.dropped_files.clone());
        if !dropped.is_empty() && !self.busy {
            let paths: Vec<PathBuf> = dropped.into_iter().filter_map(|f| f.path).collect();
            self.add_paths(paths);
        }
        ctx.request_repaint_after(std::time::Duration::from_millis(150));
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.add_space(4.0);
            ui.horizontal(|ui| {
                ui.label(RichText::new("TCDOVERLORD").strong().size(13.0).color(Color32::from_rgb(79, 156, 255)));
                ui.with_layout(Layout::right_to_left(Align::Center), |ui| {
                    ui.label(RichText::new("LOCAL | PRIVATE | OFFLINE").small().color(Color32::from_rgb(110, 190, 150)));
                });
            });
            ui.add_space(8.0);
            ui.heading(RichText::new("HEIC TO JPG").size(30.0).strong());
            ui.label("Convert up to 20 iPhone photos at a time. Your originals stay untouched.");
            ui.add_space(14.0);

            let drop_frame = egui::Frame::group(ui.style()).stroke(Stroke::new(1.5_f32, Color32::from_rgb(67, 133, 230))).inner_margin(egui::Margin::same(18));
            drop_frame.show(ui, |ui| {
                ui.set_min_height(112.0);
                ui.vertical_centered(|ui| {
                    ui.add_space(8.0);
                    ui.label(RichText::new("DROP FILES").size(20.0).color(Color32::from_rgb(79, 156, 255)));
                    ui.label(RichText::new("Drag & drop HEIC / HEIF photos here").strong().size(17.0));
                    ui.label(format!("{} / {} selected", self.files.len(), MAX_FILES));
                    ui.add_space(6.0);
                    ui.horizontal(|ui| {
                        if ui.button("Select Files").clicked() && !self.busy { self.choose_files(); }
                        if ui.button("Add Folder").clicked() && !self.busy { self.choose_folder(); }
                        if ui.button("Clear list").clicked() && !self.busy { self.files.clear(); self.status = "The file list is empty.".into(); }
                    });
                });
            });
            ui.add_space(12.0);

            ui.horizontal(|ui| {
                ui.label(RichText::new("DESTINATION FOLDER").small().strong());
            });
            ui.horizontal(|ui| {
                ui.add_enabled(!self.busy, egui::TextEdit::singleline(&mut self.output).desired_width(f32::INFINITY).hint_text("Choose where your JPG files should go"));
                if ui.add_enabled(!self.busy, egui::Button::new("Browse...")).clicked() { self.choose_output(); }
            });
            ui.add_space(6.0);
            ui.horizontal(|ui| {
                ui.label("JPG quality");
                ui.add_enabled(!self.busy, egui::Slider::new(&mut self.quality, 70..=100).suffix("%").show_value(true));
                ui.label(RichText::new("Existing JPGs are safely renamed").small().color(Color32::GRAY));
            });
            ui.add_space(10.0);

            ui.label(RichText::new("FILES TO CONVERT").small().strong());
            egui::Frame::group(ui.style()).show(ui, |ui| {
                ScrollArea::vertical().max_height(190.0).auto_shrink([false, true]).show(ui, |ui| {
                    if self.files.is_empty() {
                        ui.vertical_centered(|ui| { ui.add_space(20.0); ui.label(RichText::new("No photos added yet").color(Color32::GRAY)); ui.label(RichText::new("Drop files above or use Select files").small().color(Color32::GRAY)); ui.add_space(20.0); });
                    } else {
                        let mut remove_at = None;
                        for (idx, item) in self.files.iter().enumerate() {
                            ui.horizontal(|ui| {
                                ui.label(RichText::new(match item.status.as_str() { "Done" => "OK", "Failed" => "!", "Queued" => "â—·", _ => "â–§" }).color(match item.status.as_str() { "Done" => Color32::from_rgb(80, 190, 125), "Failed" => Color32::from_rgb(230, 90, 90), _ => Color32::LIGHT_BLUE }));
                                ui.vertical(|ui| {
                                    ui.label(RichText::new(item.path.file_name().unwrap_or_default().to_string_lossy()).strong());
                                    ui.label(RichText::new(format!("{} Â· {}", item.status, item.detail)).small().color(Color32::GRAY));
                                });
                                ui.with_layout(Layout::right_to_left(Align::Center), |ui| {
                                    if ui.add_enabled(!self.busy, egui::Button::new("Ã—")).clicked() { remove_at = Some(idx); }
                                });
                            });
                            ui.separator();
                        }
                        if let Some(idx) = remove_at { self.files.remove(idx); }
                    }
                });
            });
            ui.add_space(12.0);
            ui.horizontal(|ui| {
                if ui.add_enabled(!self.busy && !self.files.is_empty(), egui::Button::new(RichText::new("Convert to JPG").strong()).min_size(egui::vec2(160.0, 38.0))).clicked() { self.start(); }
                if self.busy { ui.spinner(); ui.label("Working..."); }
                ui.with_layout(Layout::right_to_left(Align::Center), |ui| {
                    ui.label(format!("{} converted Â· {} failed", self.completed, self.failed));
                });
            });
            ui.add_space(8.0);
            ui.separator();
            ui.label(RichText::new(&self.status).color(if self.failed > 0 && !self.busy { Color32::from_rgb(230, 150, 100) } else { Color32::LIGHT_GRAY }));
            ui.add_space(4.0);
            ui.label(RichText::new("No uploads. No source deletion. Output files are created locally.").small().color(Color32::GRAY));
        });
    }
}

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([790.0, 760.0])
            .with_min_inner_size([650.0, 620.0])
            .with_title(APP_TITLE),
        ..Default::default()
    };
    eframe::run_native(APP_TITLE, options, Box::new(|cc| {
        cc.egui_ctx.set_visuals(egui::Visuals::dark());
        Ok(Box::<ConverterApp>::default())
    }))
}

fn is_heic(path: &Path) -> bool {
    matches!(path.extension().and_then(|s| s.to_str()).unwrap_or("").to_ascii_lowercase().as_str(), "heic" | "heif")
}

fn canonical_or_original(path: &Path) -> PathBuf { fs::canonicalize(path).unwrap_or_else(|_| path.to_path_buf()) }

fn convert_one(source: &Path, output_dir: &Path, quality: u8) -> anyhow::Result<PathBuf> {
    if !source.is_file() { anyhow::bail!("Input file no longer exists."); }
    fs::create_dir_all(output_dir)?;

    let lib = LibHeif::new();
    let ctx = HeifContext::read_from_file(source.to_string_lossy().as_ref())?;
    let handle = ctx.primary_image_handle()?;
    let image = lib.decode(&handle, ColorSpace::Rgb(RgbChroma::Rgb), None)?;
    let planes = image.planes();
    let plane = planes.interleaved.ok_or_else(|| anyhow::anyhow!("Decoder returned no RGB pixel plane."))?;
    let width = image.width() as usize;
    let height = image.height() as usize;
    let stride = plane.stride;
    let bytes = plane.data;
    let mut rgb = ImageBuffer::<Rgb<u8>, Vec<u8>>::new(width as u32, height as u32);
    for y in 0..height {
        for x in 0..width {
            let i = y * stride + x * 3;
            if i + 2 >= bytes.len() { anyhow::bail!("Image pixel data is truncated."); }
            rgb.put_pixel(x as u32, y as u32, Rgb([bytes[i], bytes[i + 1], bytes[i + 2]]));
        }
    }
    let image = DynamicImage::ImageRgb8(rgb);
    let stem = source.file_stem().unwrap_or_default().to_string_lossy();
    let mut target = output_dir.join(format!("{stem}.jpg"));
    let mut suffix = 1u32;
    while target.exists() {
        target = output_dir.join(format!("{stem}_{suffix}.jpg"));
        suffix += 1;
    }
    let temp = output_dir.join(format!(".{stem}.{}.tmp.jpg", std::process::id()));
    let save = (|| -> anyhow::Result<()> {
        let file = fs::File::create(&temp)?;
        let mut writer = std::io::BufWriter::new(file);
        let mut encoder = image::codecs::jpeg::JpegEncoder::new_with_quality(&mut writer, quality);
        encoder.encode_image(&image)?;
        writer.flush()?;
        Ok(())
    })();
    if let Err(e) = save { let _ = fs::remove_file(&temp); return Err(e); }
    if target.exists() { let _ = fs::remove_file(&temp); anyhow::bail!("Destination appeared during conversion; no existing file was overwritten."); }
    fs::rename(&temp, &target).map_err(|e| { let _ = fs::remove_file(&temp); anyhow::anyhow!(e) })?;
    Ok(target)
}
