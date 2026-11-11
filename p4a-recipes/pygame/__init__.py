# -*- coding: utf-8 -*-
# Локальный рецепт pygame для p4a: фикс pygame issue #4394.
# На ARM64 pygame включает NEON-ускорение блиттеров (PG_ENABLE_ARM_NEON),
# но в Setup для Android не указан файл src_c/simd_blitters_sse2.c,
# где эти функции реализованы -> surface.so не загружается:
# ImportError: cannot locate symbol "alphablit_alpha_sse2_argb_surf_alpha".
# Патч дописывает недостающий файл к модулю surface.

import os
from os.path import join

try:
    # новые версии p4a (master)
    from pythonforandroid.recipes.pygame import PygameRecipe as BasePygameRecipe
except ImportError:
    # старые версии p4a (develop и ранее)
    from pythonforandroid.recipes.pygame import Pygame2Recipe as BasePygameRecipe

MISSING_SOURCE = "src_c/simd_blitters_sse2.c"


def _patch_setup(content):
    if MISSING_SOURCE in content:
        return content  # уже пропатчен — идемпотентно
    out = []
    patched = False
    for line in content.splitlines():
        if line.startswith("surface "):
            line = line.rstrip() + " " + MISSING_SOURCE
            patched = True
        out.append(line)
    if not patched:
        print("[recipe-patch] WARNING: line 'surface ...' not found, patch not applied")
        return content
    return "\n".join(out) + "\n"


class PatchedPygameRecipe(BasePygameRecipe):
    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        build_dir = self.get_build_dir(arch.arch)
        # в новых версиях p4a файл Setup уже сгенерирован в prebuild,
        # в старых он создаётся позже из шаблона — патчим оба варианта
        candidates = ["Setup", join("buildconfig", "Setup.Android.SDL2.in")]
        for name in candidates:
            path = join(build_dir, name)
            if not os.path.exists(path):
                continue
            with open(path) as f:
                content = f.read()
            patched = _patch_setup(content)
            if patched != content:
                with open(path, "w") as f:
                    f.write(patched)
                print("[recipe-patch] applied:", name)


recipe = PatchedPygameRecipe()
