#!/usr/bin/env python3

"""Regenerate README previews from a VS Code checkout or Git ref."""

import argparse
import io
import re
import subprocess
from pathlib import Path
from typing import Callable

from PIL import Image, ImageChops, ImageDraw, ImageFont


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PET_ROOT = Path('src/vs/workbench/contrib/chat/browser/widget/media/chatPet')
WIDGET_PATH = Path('src/vs/workbench/contrib/chat/browser/widget/chatPetWidget.ts')

parser = argparse.ArgumentParser(description='Regenerate the vscode-chat-pet README previews from VS Code sources.')
parser.add_argument('--vscode-root', type=Path, default=REPOSITORY_ROOT.parent / 'vscode', help='Path to a microsoft/vscode checkout.')
parser.add_argument('--ref', help='Optional Git ref to read without checking it out, for example refs/remotes/origin/pr-330399.')
parser.add_argument('--only', nargs='+', metavar='PREVIEW', help='Only regenerate named previews, with or without the .png suffix.')
args = parser.parse_args()

VSCODE_ROOT = args.vscode_root.resolve()
OUTPUT_ROOT = REPOSITORY_ROOT / 'readme-assets'


def source_bytes(path: Path) -> bytes:
	if args.ref:
		return subprocess.check_output(['git', '-C', str(VSCODE_ROOT), 'show', f'{args.ref}:{path.as_posix()}'])
	return (VSCODE_ROOT / path).read_bytes()


def source_text(path: Path) -> str:
	return source_bytes(path).decode('utf-8')


def source_image(filename: str) -> Image.Image:
	return Image.open(io.BytesIO(source_bytes(PET_ROOT / filename)))


widget_source = source_text(WIDGET_PATH)


def source_number(name: str, default: int) -> int:
	match = re.search(rf'const {re.escape(name)} = (\d[\d_]*)', widget_source)
	return int(match.group(1).replace('_', '')) if match else default


def source_durations(name: str, default: list[int]) -> list[int]:
	array_match = re.search(rf'const {re.escape(name)} = \[([^\]]+)\]', widget_source)
	if array_match:
		return [int(value.replace('_', '').strip()) for value in array_match.group(1).split(',') if value.strip()]
	repeated_match = re.search(rf'const {re.escape(name)} = Array\.from\(\{{ length: (\d+) \}}, \(\) => (\d[\d_]*)\)', widget_source)
	if repeated_match:
		return [int(repeated_match.group(2).replace('_', ''))] * int(repeated_match.group(1))
	return default

FRAME_DURATION = 100
STANDARD_SIZE = (500, 200)
MOVEMENT_SIZE = (500, 260)
PANEL_MARGIN = 8
PANEL_GAP = 8
PANEL_WIDTH = 238
PANEL_TOP = 28

FONT = ImageFont.truetype('/System/Library/Fonts/SFNS.ttf', 12)
FONT_BOLD = ImageFont.truetype('/System/Library/Fonts/SFNS.ttf', 13)

BACKGROUND = '#181818'
PANEL_BACKGROUND = '#1f1f1f'
PANEL_BORDER = '#3f3f46'
PLATFORM_BACKGROUND = '#2b2b2b'
PLATFORM_BORDER = '#555555'
FOREGROUND = '#cccccc'
CURSOR_FILL = '#f4f4f4'
CURSOR_BORDER = '#181818'
PUPIL = '#191a1b'
STABLE_ACCENT = '#007acc'
INSIDERS_ACCENT = '#25bda7'

IDLE_DURATIONS = source_durations('IDLE_FRAME_DURATIONS', [40] * 50)
SLEEP_DURATIONS = source_durations('SLEEP_FRAME_DURATIONS', [300] * 8)
WAKE_DURATIONS = source_durations('WAKE_FRAME_DURATIONS', [160, 100, 80, 90, 90, 90, 100, 170])
TYPING_DURATIONS = source_durations('TYPING_FRAME_DURATIONS', [400, 600])
BUTTON_DURATIONS = source_durations('BUTTON_PRESS_FRAME_DURATIONS', [500, 300, 350, 250, 450, 1_000])
FALLING_DURATIONS = source_durations('FALLING_FRAME_DURATIONS', [120] * 4)
JUMP_DURATIONS = source_durations('JUMP_FRAME_DURATIONS', [70, 80, 90, 160, 100, 100])
SPLAT_DURATIONS = source_durations('SPLAT_FRAME_DURATIONS', [120, 100, 100, 200])
RESPAWN_DURATIONS = source_durations('RESPAWN_FRAME_DURATIONS', [120, 100, 120, 240, 100, 120])
SPEECH_DURATIONS = source_durations('SPEECH_FRAME_DURATIONS', [220, 220, 220, 100, 160, 180])
CLAPPING_DURATIONS = source_durations('CLAPPING_FRAME_DURATIONS', [80, 40, 40, 40, 80, 40, 40, 40, 40, 80, 40, 40, 80])
LOVE_DURATIONS = source_durations('LOVE_FRAME_DURATIONS', [200, 200, 380, 100, 80, 1_980])
COOL_DURATIONS = source_durations('COOL_FRAME_DURATIONS', [600, 120, 120, 120, 160, 80, 80, 80, 1_640])
SING_DURATIONS = source_durations('SING_FRAME_DURATIONS', [180] * 4)
SPEECHLESS_DURATIONS = source_durations('SPEECHLESS_FRAME_DURATIONS', [400, 120, 1_000, 120, 1_080])
WORRY_DURATIONS = source_durations('WORRY_FRAME_DURATIONS', [600, 600])
DIZZY_DURATIONS = source_durations('DIZZY_FRAME_DURATIONS', [120] * 8)
SEARCH_DURATIONS = source_durations('SEARCH_FRAME_DURATIONS', [500] * 4)

SLEEP_SOURCE_WIDTH = source_number('CHAT_PET_SLEEP_SOURCE_WIDTH', 96)
TYPING_SOURCE_WIDTH = source_number('CHAT_PET_TYPING_SOURCE_WIDTH', 168)

SPRITES = {
	'idle': ('buddy-idle-{variant}-tracking-96', 96, 96, IDLE_DURATIONS, True),
	'sleep': ('buddy-sleep-{variant}-96', SLEEP_SOURCE_WIDTH, 96, SLEEP_DURATIONS, False),
	'waking': ('buddy-waking-{variant}-96', SLEEP_SOURCE_WIDTH, 96, WAKE_DURATIONS, False),
	'typing': ('buddy-typing-{variant}-96', TYPING_SOURCE_WIDTH, 96, TYPING_DURATIONS, False),
	'rendering': ('buddy-rendering-{variant}-tracking-96', 96, 96, IDLE_DURATIONS, True),
	'button': ('buddy-press-button-{variant}-96', 160, 96, BUTTON_DURATIONS, False),
	'love': ('buddy-love-{variant}-96', 96, 96, LOVE_DURATIONS, False),
	'clapping': ('buddy-clapping-{variant}-tracking-96', 96, 96, CLAPPING_DURATIONS, True),
	'jump': ('buddy-jump-{variant}-96', 96, 96, JUMP_DURATIONS, False),
	'cool': ('buddy-cool-{variant}-96', 96, 96, COOL_DURATIONS, False),
	'sing': ('buddy-sing-{variant}-124', 164, 124, SING_DURATIONS, False),
	'speechless': ('buddy-speechless-{variant}-96', 96, 96, SPEECHLESS_DURATIONS, False),
	'worry': ('buddy-worry-{variant}-96', 96, 96, WORRY_DURATIONS, False),
	'dizzy': ('buddy-dizzy-{variant}-128', 96, 128, DIZZY_DURATIONS, False),
	'falling': ('buddy-falling-{variant}-96', 96, 96, FALLING_DURATIONS, False),
	'splat': ('buddy-splat-{variant}-96', 96, 96, SPLAT_DURATIONS, False),
	'search': ('buddy-search-{variant}-96', 96, 96, SEARCH_DURATIONS, False),
	'speech': ('buddy-speech-{variant}-96', 96, 96, SPEECH_DURATIONS, False),
	'respawn': ('buddy-respawn-{variant}-96', 96, 96, RESPAWN_DURATIONS, False),
}

_frames: dict[tuple[str, str], list[Image.Image]] = {}


def clamp(value: float, minimum: float, maximum: float) -> float:
	return max(minimum, min(maximum, value))


def ease_out(value: float) -> float:
	return 1 - (1 - clamp(value, 0, 1)) ** 3


def ease_in(value: float) -> float:
	return clamp(value, 0, 1) ** 2


def interpolate(start: float, end: float, progress: float) -> float:
	return start + (end - start) * progress


def frame_index(durations: list[int], elapsed: float, loop: bool = True) -> int:
	total = sum(durations)
	elapsed = elapsed % total if loop else clamp(elapsed, 0, total - 1)
	accumulated = 0
	for index, duration in enumerate(durations):
		accumulated += duration
		if elapsed < accumulated:
			return index
	return len(durations) - 1


def source_frames(state: str, variant: str) -> list[Image.Image]:
	key = (state, variant)
	if key in _frames:
		return _frames[key]
	name, width, height, _, _ = SPRITES[state]
	with source_image(f'{name.format(variant=variant)}.spritesheet.png') as image:
		source = image.convert('RGBA')
		_frames[key] = [
			source.crop((left, 0, left + width, height))
			for left in range(0, source.width, width)
		]
	return _frames[key]


def sprite(state: str, variant: str, elapsed: float = 0, loop: bool = True, gaze: tuple[int, int] = (0, 0), dragging: bool = False, reverse: bool = False) -> Image.Image:
	_, _, _, durations, tracking = SPRITES[state]
	frames = source_frames(state, variant)
	index = min(frame_index(durations, elapsed, loop), len(frames) - 1)
	result = frames[len(frames) - 1 - index if reverse else index].copy()
	if tracking:
		add_tall_eyes(result, elapsed, gaze, dragging)
	return result


def add_tall_eyes(image: Image.Image, elapsed: float, gaze: tuple[int, int], dragging: bool) -> None:
	draw = ImageDraw.Draw(image)
	bob = 4 if elapsed % 2_000 >= 800 else 0
	if dragging:
		for center_x in (44, 68):
			center_y = 70 + bob
			draw.line((center_x - 8, center_y - 4, center_x + 8, center_y + 4), fill=PUPIL, width=4)
			draw.line((center_x - 8, center_y + 4, center_x + 8, center_y - 4), fill=PUPIL, width=4)
		return
	delta_x, delta_y = gaze
	blink = 920 <= elapsed % 2_000 < 1_120
	height = 4 if blink else 16
	y = 64 + bob + delta_y + (6 if blink else 0)
	for x in (40, 64):
		draw.rectangle((x + delta_x, y, x + delta_x + 7, y + height - 1), fill=PUPIL)


def panel_left(index: int) -> int:
	return PANEL_MARGIN + index * (PANEL_WIDTH + PANEL_GAP)


def body_left(index: int) -> int:
	return panel_left(index) + (PANEL_WIDTH - 96) // 2


def centered_frame_left(index: int, width: int) -> int:
	return panel_left(index) + (PANEL_WIDTH - width) // 2


def canvas(size: tuple[int, int]) -> Image.Image:
	result = Image.new('RGBA', size, BACKGROUND)
	draw = ImageDraw.Draw(result)
	panel_bottom = size[1] - 8
	for index, (label, accent) in enumerate((('STABLE', STABLE_ACCENT), ('INSIDERS', INSIDERS_ACCENT))):
		left = panel_left(index)
		draw.rounded_rectangle((left, PANEL_TOP, left + PANEL_WIDTH, panel_bottom), radius=8, fill=PANEL_BACKGROUND, outline=PANEL_BORDER)
		draw.ellipse((left + 8, 10, left + 16, 18), fill=accent)
		draw.text((left + 22, 8), label, fill=FOREGROUND, font=FONT_BOLD)
	return result


def draw_platform(image: Image.Image, index: int, top: int, left_inset: int = 18, right_inset: int = 18) -> tuple[int, int]:
	draw = ImageDraw.Draw(image)
	left = panel_left(index) + left_inset
	right = panel_left(index) + PANEL_WIDTH - right_inset
	draw.rounded_rectangle((left, top, right, top + 9), radius=4, fill=PLATFORM_BACKGROUND, outline=PLATFORM_BORDER)
	return left, right


def draw_badge(image: Image.Image, index: int, label: str) -> None:
	draw = ImageDraw.Draw(image)
	left = panel_left(index) + 14
	top = PANEL_TOP + 14
	bounds = draw.textbbox((0, 0), label, font=FONT)
	width = bounds[2] - bounds[0] + 16
	draw.rounded_rectangle((left, top, left + width, top + 23), radius=5, fill='#2d2d30', outline='#666666')
	draw.text((left + 8, top + 4), label, fill=FOREGROUND, font=FONT)


def draw_keycap(image: Image.Image, index: int, label: str) -> None:
	draw = ImageDraw.Draw(image)
	left = panel_left(index) + 18
	top = PANEL_TOP + 14
	draw.rounded_rectangle((left, top, left + 28, top + 24), radius=4, fill='#2d2d30', outline='#666666')
	bounds = draw.textbbox((0, 0), label, font=FONT_BOLD)
	draw.text((left + (28 - (bounds[2] - bounds[0])) / 2, top + 3), label, fill=FOREGROUND, font=FONT_BOLD)


def draw_cursor(image: Image.Image, left: float, top: float, pressed: bool = False) -> None:
	draw = ImageDraw.Draw(image)
	points = [(left, top), (left + 1, top + 23), (left + 7, top + 17), (left + 12, top + 28), (left + 17, top + 26), (left + 12, top + 15), (left + 21, top + 14)]
	draw.polygon(points, fill=CURSOR_FILL, outline=CURSOR_BORDER)
	if pressed:
		draw.ellipse((left - 8, top - 8, left + 30, top + 30), outline='#ffffff88', width=2)


def paste(image: Image.Image, art: Image.Image, left: float, top: float, scale: float = 1, angle: float = 0, opacity: float = 1) -> None:
	if scale != 1:
		art = art.resize((round(art.width * scale), round(art.height * scale)), Image.Resampling.NEAREST)
	if angle:
		art = art.rotate(angle, resample=Image.Resampling.NEAREST, expand=True)
	if opacity < 1:
		art.putalpha(art.getchannel('A').point(lambda value: round(value * opacity)))
	image.alpha_composite(art, (round(left), round(top)))


def draw_toggle(image: Image.Image, index: int, variant: str, elapsed: float) -> None:
	draw_platform(image, index, 176)
	left = body_left(index)
	if elapsed < 500 or elapsed >= 2_200:
		return
	if elapsed < 900:
		progress = ease_out((elapsed - 500) / 400)
		scale = interpolate(0.5, 1, progress)
		top = interpolate(104, 80, progress)
		opacity = progress
	elif elapsed < 1_800:
		scale, top, opacity = 1, 80, 1
	else:
		progress = ease_in((elapsed - 1_800) / 400)
		scale = interpolate(1, 0.55, progress)
		top = interpolate(80, 108, progress)
		opacity = 1 - progress
	art = sprite('idle', variant, elapsed, gaze=(1, -1))
	scaled = art.resize((round(96 * scale), round(96 * scale)), Image.Resampling.NEAREST)
	paste(image, scaled, left + (96 - scaled.width) / 2, top + (96 - scaled.height), opacity=opacity)


def draw_gaze(image: Image.Image, index: int, variant: str, elapsed: float) -> None:
	import math
	draw_platform(image, index, 176)
	left, top = body_left(index), 80
	phase = elapsed / 3_000 * 2 * math.pi
	cursor_x = left + 48 + 72 * math.cos(phase)
	cursor_y = top + 48 + 46 * math.sin(phase)
	gaze = (
		round(clamp((cursor_x - (left + 48)) / 18, -4, 4)),
		round(clamp((cursor_y - (top + 48)) / 18, -4, 4)),
	)
	paste(image, sprite('idle', variant, elapsed, gaze=gaze), left, top)
	draw_cursor(image, cursor_x, cursor_y)


def draw_processing(image: Image.Image, index: int, variant: str, elapsed: float) -> None:
	draw_platform(image, index, 176)
	left, top = body_left(index) - 16, 80
	bubble = sprite('speech', variant, elapsed).resize((144, 144), Image.Resampling.NEAREST)
	paste(image, bubble, left + 8, top - 60)
	paste(image, sprite('rendering', variant, elapsed, gaze=(3, -2)), left, top)


def draw_typing(image: Image.Image, index: int, variant: str, elapsed: float) -> None:
	draw_platform(image, index, 176)
	draw_badge(image, index, 'Typing')
	art = sprite('typing', variant, elapsed)
	paste(image, art, centered_frame_left(index, TYPING_SOURCE_WIDTH), 176 - art.height)


def draw_clapping(image: Image.Image, index: int, variant: str, elapsed: float) -> None:
	draw_platform(image, index, 176)
	draw_badge(image, index, 'Needs input')
	paste(image, sprite('clapping', variant, elapsed, gaze=(0, -2)), body_left(index), 80)


def draw_sleep_wake(image: Image.Image, index: int, variant: str, elapsed: float) -> None:
	draw_platform(image, index, 176)
	wide_left = centered_frame_left(index, SLEEP_SOURCE_WIDTH)
	idle_left = body_left(index)
	if elapsed < 2_000:
		paste(image, sprite('sleep', variant, elapsed), wide_left, 80)
	elif elapsed < 2_300:
		paste(image, sprite('sleep', variant, elapsed), wide_left, 80)
		draw_cursor(image, idle_left + 58, 116, elapsed >= 2_150)
	elif elapsed < 3_180:
		paste(image, sprite('waking', variant, elapsed - 2_300, False), wide_left, 80)
	else:
		paste(image, sprite('idle', variant, elapsed - 3_180, gaze=(2, -1)), idle_left, 80)


def reaction(state: str, reaction_start: int, reaction_duration: int, loop: bool, frame_width: int = 96) -> Callable:
	def renderer(image: Image.Image, index: int, variant: str, elapsed: float) -> None:
		draw_platform(image, index, 176)
		left = centered_frame_left(index, frame_width)
		if elapsed < reaction_start:
			paste(image, sprite('idle', variant, elapsed), left, 80)
		elif elapsed < reaction_start + reaction_duration:
			art = sprite(state, variant, elapsed - reaction_start, loop)
			paste(image, art, left, 176 - art.height)
		else:
			paste(image, sprite('idle', variant, elapsed - reaction_start - reaction_duration), left, 80)
		progress = clamp((elapsed - 250) / 400, 0, 1)
		if 250 <= elapsed <= 1_050:
			draw_cursor(
				image,
				interpolate(panel_left(index) + PANEL_WIDTH - 38, left + 56, ease_out(progress)),
				interpolate(58, 116, ease_out(progress)),
				680 <= elapsed <= 860,
			)
	return renderer


def draw_keyboard_hop(image: Image.Image, index: int, variant: str, elapsed: float) -> None:
	import math
	draw_platform(image, index, 176)
	left = body_left(index)
	if elapsed < 500:
		draw_keycap(image, index, '→')
		paste(image, sprite('idle', variant, elapsed), left, 80)
	elif elapsed < 1_100:
		progress = (elapsed - 500) / 600
		paste(image, sprite('jump', variant, elapsed - 500, False), left + 48 * progress, 80 - 22 * math.sin(progress * math.pi))
		draw_keycap(image, index, '→')
	elif elapsed < 1_600:
		paste(image, sprite('idle', variant, elapsed), left + 48, 80)
	elif elapsed < 2_200:
		progress = (elapsed - 1_600) / 600
		art = sprite('jump', variant, elapsed - 1_600, False).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
		paste(image, art, left + 48 * (1 - progress), 80 - 22 * math.sin(progress * math.pi))
		draw_keycap(image, index, '←')
	else:
		paste(image, sprite('idle', variant, elapsed), left, 80)


def paste_dragging(image: Image.Image, art: Image.Image, left: float, top: float, elapsed: float, strong: bool) -> None:
	step = 100 if strong else 200
	direction = -1 if int(elapsed / step) % 2 == 0 else 1
	distance, angle = (2, 2) if strong else (1, 1)
	rotated = art.rotate(direction * angle, resample=Image.Resampling.NEAREST, expand=True)
	paste(image, rotated, left + direction * distance - (rotated.width - art.width) / 2, top - (rotated.height - art.height) / 2)


def draw_drag_drop(image: Image.Image, index: int, variant: str, elapsed: float) -> None:
	platform_top = 222
	platform_left, platform_right = draw_platform(image, index, platform_top, 26, 26)
	start_left, target_left = platform_right - 112, platform_left + 12
	start_top, pickup_top = platform_top - 96, 54
	if elapsed < 450:
		paste(image, sprite('idle', variant, elapsed), start_left, start_top)
		draw_cursor(image, start_left + 52, start_top + 38)
	elif elapsed < 1_350:
		progress = ease_out((elapsed - 450) / 900)
		x, y = interpolate(start_left, target_left, progress), interpolate(start_top, pickup_top, progress)
		paste_dragging(image, sprite('idle', variant, elapsed, dragging=True), x, y, elapsed - 450, False)
		draw_cursor(image, x + 52, y + 38, True)
	elif elapsed < 1_650:
		progress = ease_in((elapsed - 1_350) / 300)
		paste(image, sprite('falling', variant, elapsed - 1_350), target_left, interpolate(pickup_top, start_top, progress))
	elif elapsed < 2_170:
		paste(image, sprite('splat', variant, elapsed - 1_650, False), target_left, start_top)
	else:
		paste(image, sprite('idle', variant, elapsed - 2_170), target_left, start_top)


def draw_fall_respawn(image: Image.Image, index: int, variant: str, elapsed: float) -> None:
	platform_top = 208
	platform_left, platform_right = draw_platform(image, index, platform_top, 88, 18)
	start_left, start_top = platform_right - 106, platform_top - 96
	edge_left, floor_top = platform_left - 76, MOVEMENT_SIZE[1] - 8 - 96
	spawn_left, spawn_top = platform_right - 110, 42
	if elapsed < 450:
		paste(image, sprite('idle', variant, elapsed), start_left, start_top)
		draw_cursor(image, start_left + 52, start_top + 38)
	elif elapsed < 1_250:
		progress = ease_out((elapsed - 450) / 800)
		x, y = interpolate(start_left, edge_left, progress), interpolate(start_top, 58, progress)
		paste_dragging(image, sprite('idle', variant, elapsed, dragging=True), x, y, elapsed - 450, True)
		draw_cursor(image, x + 52, y + 38, True)
	elif elapsed < 1_550:
		progress = ease_in((elapsed - 1_250) / 300)
		paste(image, sprite('falling', variant, elapsed - 1_250), edge_left, interpolate(58, floor_top, progress))
	elif elapsed < 2_350:
		paste(image, sprite('respawn', variant, elapsed - 1_550, False, reverse=True), edge_left, floor_top)
	elif elapsed < 3_150:
		paste(image, sprite('respawn', variant, elapsed - 2_350, False), spawn_left, spawn_top)
	elif elapsed < 3_550:
		progress = ease_in((elapsed - 3_150) / 400)
		paste(image, sprite('falling', variant, elapsed - 3_150), spawn_left, interpolate(spawn_top, start_top, progress))
	elif elapsed < 4_070:
		paste(image, sprite('splat', variant, elapsed - 3_550, False), spawn_left, start_top)
	else:
		paste(image, sprite('idle', variant, elapsed - 4_070), spawn_left, start_top)


def paste_above_platform(image: Image.Image, art: Image.Image, left: int, top: float, platform_top: int) -> None:
	top = round(top)
	height = min(art.height, platform_top - top)
	if height > 0:
		paste(image, art.crop((0, 0, art.width, height)), left, top)


def draw_on_the_run(image: Image.Image, index: int, variant: str, elapsed: float) -> None:
	platform_top = 150
	left, resting_top, hidden_top, peek_top = body_left(index), 54, 150, 70
	draw_badge(image, index, 'Go on the Run' if elapsed < 2_950 else 'Come Back')
	if elapsed < 500:
		paste_above_platform(image, sprite('idle', variant, elapsed), left, resting_top, platform_top)
	elif elapsed < 900:
		paste_above_platform(image, sprite('idle', variant, elapsed), left, interpolate(resting_top, hidden_top, ease_in((elapsed - 500) / 400)), platform_top)
	elif elapsed < 1_300:
		pass
	elif elapsed < 1_650:
		paste_above_platform(image, sprite('search', variant, elapsed - 1_300), left, interpolate(hidden_top, peek_top, ease_out((elapsed - 1_300) / 350)), platform_top)
	elif elapsed < 2_650:
		paste_above_platform(image, sprite('search', variant, elapsed - 1_300), left, peek_top, platform_top)
	elif elapsed < 2_950:
		paste_above_platform(image, sprite('search', variant, elapsed - 1_300), left, interpolate(peek_top, hidden_top, ease_in((elapsed - 2_650) / 300)), platform_top)
	elif elapsed < 3_350:
		pass
	elif elapsed < 3_750:
		paste_above_platform(image, sprite('idle', variant, elapsed), left, interpolate(hidden_top, resting_top, ease_out((elapsed - 3_350) / 400)), platform_top)
	else:
		paste_above_platform(image, sprite('idle', variant, elapsed), left, resting_top, platform_top)
	draw_platform(image, index, platform_top, 28, 28)


def draw_resize(image: Image.Image, index: int, variant: str, elapsed: float) -> None:
	draw_platform(image, index, 176)
	if elapsed < 700:
		scale, label = 1, 'Grow'
	elif elapsed < 1_500:
		scale, label = interpolate(1, 1.4, ease_out((elapsed - 700) / 800)), 'Grow'
	elif elapsed < 2_200:
		scale, label = 1.4, 'Shrink'
	elif elapsed < 3_000:
		scale, label = interpolate(1.4, 0.6, ease_out((elapsed - 2_200) / 800)), 'Shrink'
	else:
		scale, label = interpolate(0.6, 1, ease_out((elapsed - 3_000) / 700)), 'Reset'
	draw_badge(image, index, label)
	art = sprite('idle', variant, elapsed)
	scaled = art.resize((round(96 * scale), round(96 * scale)), Image.Resampling.NEAREST)
	paste(image, scaled, body_left(index) + (96 - scaled.width) / 2, 176 - scaled.height)


def draw_dizzy(image: Image.Image, index: int, variant: str, elapsed: float) -> None:
	draw_platform(image, index, 176)
	left = body_left(index)
	trigger_start, dizzy_start, dizzy_end = 300, 1_300, 3_500
	if elapsed < trigger_start:
		paste(image, sprite('idle', variant, elapsed), left, 80)
		draw_cursor(image, left + 95, 105)
	elif elapsed < dizzy_start:
		step = int((elapsed - trigger_start) / 100)
		facing_left = step % 2 == 1
		art = sprite('idle', variant, elapsed, gaze=(-4 if facing_left else 4, -1))
		if facing_left:
			art = art.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
		paste(image, art, left, 80)
		cursor_x = left - 28 if facing_left else left + 104
		draw_cursor(image, cursor_x, 105)
	elif elapsed < dizzy_end:
		art = sprite('dizzy', variant, elapsed - dizzy_start)
		paste(image, art, left, 176 - art.height)
	else:
		paste(image, sprite('idle', variant, elapsed - dizzy_end), left, 80)


def collapse_identical(frames: list[Image.Image], durations: list[int]) -> tuple[list[Image.Image], list[int]]:
	result_frames: list[Image.Image] = []
	result_durations: list[int] = []
	for frame, duration in zip(frames, durations):
		if result_frames and ImageChops.difference(result_frames[-1].convert('RGB'), frame.convert('RGB')).getbbox() is None:
			result_durations[-1] += duration
		else:
			result_frames.append(frame)
			result_durations.append(duration)
	return result_frames, result_durations


def save(name: str, duration: int, size: tuple[int, int], renderer: Callable) -> None:
	frames: list[Image.Image] = []
	durations: list[int] = []
	for elapsed in range(0, duration, FRAME_DURATION):
		image = canvas(size)
		for index, variant in enumerate(('stable', 'insiders')):
			renderer(image, index, variant, elapsed)
		frames.append(image)
		durations.append(FRAME_DURATION)
	frames, durations = collapse_identical(frames, durations)
	output = OUTPUT_ROOT / name
	frames[0].save(
		output,
		save_all=True,
		append_images=frames[1:],
		duration=durations,
		loop=0,
		disposal=1,
		blend=0,
		optimize=True,
	)
	print(f'{name}: {len(frames)} frames, {sum(durations)}ms, {output.stat().st_size:,} bytes')


ANIMATIONS = {
	'toggle.png': (2_800, STANDARD_SIZE, draw_toggle),
	'cursor-gaze.png': (3_000, STANDARD_SIZE, draw_gaze),
	'typing-v2.png': (3_000, STANDARD_SIZE, draw_typing),
	'processing.png': (3_000, STANDARD_SIZE, draw_processing),
	'needs-input.png': (2_200, STANDARD_SIZE, draw_clapping),
	'sleep-wake-pr330399.png': (3_800, STANDARD_SIZE, draw_sleep_wake),
	'keyboard-hop.png': (2_700, STANDARD_SIZE, draw_keyboard_hop),
	'drag-drop-v2.png': (2_900, MOVEMENT_SIZE, draw_drag_drop),
	'fall-respawn-pr330399.png': (4_700, MOVEMENT_SIZE, draw_fall_respawn),
	'click-button-v2.png': (4_200, STANDARD_SIZE, reaction('button', 800, sum(BUTTON_DURATIONS), False, 160)),
	'click-love.png': (4_300, STANDARD_SIZE, reaction('love', 800, sum(LOVE_DURATIONS), False)),
	'click-cool.png': (4_300, STANDARD_SIZE, reaction('cool', 800, sum(COOL_DURATIONS), False)),
	'click-sing-v2.png': (4_200, STANDARD_SIZE, reaction('sing', 800, 2_900, True, 164)),
	'click-speechless.png': (4_100, STANDARD_SIZE, reaction('speechless', 800, sum(SPEECHLESS_DURATIONS), False)),
	'click-worry.png': (3_700, STANDARD_SIZE, reaction('worry', 800, 2_400, True)),
	'on-the-run-v2.png': (4_300, STANDARD_SIZE, draw_on_the_run),
	'grow-shrink.png': (3_900, STANDARD_SIZE, draw_resize),
	'dizzy.png': (4_000, STANDARD_SIZE, draw_dizzy),
}


requested = None
if args.only:
	requested = {name if name.endswith('.png') else f'{name}.png' for name in args.only}
	unknown = requested - ANIMATIONS.keys()
	if unknown:
		parser.error(f'unknown preview(s): {", ".join(sorted(unknown))}')

for filename, (animation_duration, animation_size, animation_renderer) in ANIMATIONS.items():
	if requested is not None and filename not in requested:
		continue
	save(filename, animation_duration, animation_size, animation_renderer)

readme = (REPOSITORY_ROOT / 'README.md').read_text()
linked_assets = set(re.findall(r'\((readme-assets/[^)]+\.png)\)', readme))
missing_assets = sorted(asset for asset in linked_assets if not (REPOSITORY_ROOT / asset).is_file())
if missing_assets:
	raise RuntimeError(f'README references missing assets: {", ".join(missing_assets)}')

for asset in sorted(linked_assets):
	with Image.open(REPOSITORY_ROOT / asset) as image:
		if asset.endswith('click-yap-static.png'):
			if image.is_animated:
				raise RuntimeError(f'{asset} must stay static')
		elif not image.is_animated or image.info.get('loop') != 0:
			raise RuntimeError(f'{asset} must be a looping APNG')

print(f'Validated {len(linked_assets)} README image references.')
