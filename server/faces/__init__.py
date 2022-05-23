import io
import sys
import warnings

from .cosine_similarity import *  # noqa

from insightface.app import FaceAnalysis

from ..config import Config


class FaceApp(FaceAnalysis):
    def __init__(
        self, name="buffalo_l", root="~/.insightface", allowed_modules=None, **kwargs
    ):
        self.name = name
        self.root = root
        self.allowed_modules = allowed_modules
        self.kwargs = kwargs
        self.initialized = False

    def init(self):
        text_trap = io.StringIO()
        sys.stdout = text_trap

        super().__init__(
            name=self.name,
            root=self.root,
            allowed_modules=self.allowed_modules,
            **self.kwargs
        )
        super().prepare(ctx_id=0, det_thresh=0.5, det_size=(640, 640))
        self.initialized = True

        sys.stdout = sys.__stdout__

    def get(self, *args, **kwargs):
        if not self.initialized:
            self.init()

        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=FutureWarning)
            return super().get(*args, **kwargs)


face_app = FaceApp(root=Config.PUBLIC_DIR)
