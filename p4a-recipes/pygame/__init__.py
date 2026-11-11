import os
import re
from os.path import join

try:
    from pythonforandroid.recipes.pygame import Pygame2Recipe
except ImportError:
    try:
        from pythonforandroid.recipes.pygame import PygameRecipe as Pygame2Recipe
    except ImportError:
        raise ImportError("[IGLA-FIX] no pygame recipe class found in this p4a version")

MARK = "[IGLA-FIX]"
SIMD = "src_c/simd_blitters_sse2.c"
SURFACE_LINE = (
    "surface src_c/simd_blitters_sse2.c src_c/simd_blitters_avx2.c "
    "src_c/surface.c src_c/alphablit.c src_c/surface_fill.c $(SDL) $(DEBUG)"
)

# Маркер пишется в момент импорта модуля рецепта: если buildozer подхватил
# локальный рецепт, файл появится в корне репозитория независимо от лога сборки.
try:
    with open("igla_fix_marker.txt", "w") as _mf:
        _mf.write("patched pygame recipe imported OK (local recipe picked up)\n")
except OSError:
    pass


def patch_text(content):
    """Возвращает (новый текст, статус): replaced / already-patched / no-surface-line."""
    if SIMD in content:
        return content, "already-patched"
    new, n = re.subn(r"(?m)^[ \t]*surface\b[ \t].*$", SURFACE_LINE, content)
    return (new, "replaced") if n == 1 else (content, "no-surface-line")


class PatchedPygameRecipe(Pygame2Recipe):
    """Фикс pygame issue #4394: модуль surface ссылается на SIMD-символы,
    которых нет в сборке Android. Добавляем файл прямо в Setup."""

    def _patch_file(self, bdir, rel, phase):
        path = join(bdir, rel)
        if not os.path.exists(path):
            print(f"{MARK} {rel} not found at {phase}", flush=True)
            return None
        with open(path) as f:
            content = f.read()
        new, how = patch_text(content)
        print(f"{MARK} {rel} at {phase}: {how}", flush=True)
        if how == "replaced":
            with open(path, "w") as f:
                f.write(new)
        return new

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        bdir = self.get_build_dir(arch.arch)
        replaced = seen = 0
        for rel in ("buildconfig/Setup.Android.SDL2.in", "Setup"):
            new = self._patch_file(bdir, rel, "prebuild")
            if new is not None:
                seen += 1
                if SIMD in new:
                    replaced += 1
        if replaced == 0 and seen > 0:
            self._disable_neon(bdir)
        self._write_marker("prebuild done")

    def build_arch(self, arch):
        bdir = self.get_build_dir(arch.arch)
        ok = False
        for rel in ("buildconfig/Setup.Android.SDL2.in", "Setup"):
            new = self._patch_file(bdir, rel, "build")
            if new is not None and SIMD in new:
                ok = True
        if not ok:
            self._disable_neon(bdir)
        super().build_arch(arch)

    def _disable_neon(self, bdir):
        path = join(bdir, "src_c", "simd_blitters.h")
        if not os.path.exists(path):
            print(f"{MARK} FALLBACK FAILED: {path} not found", flush=True)
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

    def _write_marker(self, note):
        try:
            with open("igla_fix_marker.txt", "a") as mf:
                mf.write(note + "\n")
        except OSError:
            pass


recipe = PatchedPygameRecipe()
