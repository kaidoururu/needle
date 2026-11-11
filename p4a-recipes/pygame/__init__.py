import os
import re
from os.path import join

try:
    from pythonforandroid.recipes.pygame import Pygame2Recipe
except ImportError:
    from pythonforandroid.recipes.pygame import PygameRecipe as Pygame2Recipe

# Fix for pygame issue #4394 on arm64-v8a:
# pygame 2.5+ enables ARM NEON blitters, but the Android Setup template does
# not compile simd_blitters_sse2.c, so surface.so references the missing
# symbol alphablit_alpha_sse2_argb_surf_alpha and dies at import time.
# This recipe adds the missing source file to both the template and the
# generated Setup file; if the patch cannot be applied, it falls back to
# disabling NEON blitters entirely (pure-C path, visually identical).

MARK = "[IGLA-FIX]"
SIMD = "src_c/simd_blitters_sse2.c"
SURFACE_LINE = (
    "surface src_c/simd_blitters_sse2.c src_c/simd_blitters_avx2.c "
    "src_c/surface.c src_c/alphablit.c src_c/surface_fill.c $(SDL) $(DEBUG)"
)
SETUP_FILES = ("buildconfig/Setup.Android.SDL2.in", "Setup")


def patch_text(content):
    if SIMD in content:
        return content, "already-patched"
    new, n = re.subn(r"(?m)^[ \t]*surface\b[ \t].*$", SURFACE_LINE, content)
    if n == 1:
        return new, "replaced"
    return content, "no-surface-line"


def apply_patch(bdir, stage):
    """Patch the Setup files. Returns True if SIMD source is referenced."""
    simd_ok = False
    seen = 0
    for rel in SETUP_FILES:
        path = join(bdir, rel)
        if not os.path.exists(path):
            print(f"{MARK} {rel} not found at {stage}", flush=True)
            continue
        seen += 1
        with open(path) as f:
            content = f.read()
        new, how = patch_text(content)
        print(f"{MARK} {rel} at {stage}: {how}", flush=True)
        if how == "replaced":
            with open(path, "w") as f:
                f.write(new)
        if SIMD in new:
            simd_ok = True
    if seen == 0:
        print(f"{MARK} WARNING: no Setup files found at {stage}", flush=True)
    return simd_ok


def disable_neon(bdir, stage):
    path = join(bdir, "src_c", "simd_blitters.h")
    if not os.path.exists(path):
        print(f"{MARK} FALLBACK FAILED at {stage}: {path} not found", flush=True)
        return
    with open(path) as f:
        h = f.read()
    if "IGLA_DISABLE_NEON" in h:
        print(f"{MARK} FALLBACK already applied", flush=True)
        return
    h += "\n#undef PG_ENABLE_ARM_NEON /* IGLA_DISABLE_NEON */\n"
    with open(path, "w") as f:
        f.write(h)
    print(f"{MARK} FALLBACK: NEON disabled in simd_blitters.h", flush=True)


class PatchedPygameRecipe(Pygame2Recipe):
    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        bdir = self.get_build_dir(arch.arch)
        if not apply_patch(bdir, "prebuild"):
            disable_neon(bdir, "prebuild")

    def build_arch(self, arch):
        bdir = self.get_build_dir(arch.arch)
        if not apply_patch(bdir, "build"):
            disable_neon(bdir, "build")
        super().build_arch(arch)


recipe = PatchedPygameRecipe()
