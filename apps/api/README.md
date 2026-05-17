# API

FastAPI inference entrypoint for `VPCM.predict()`. The local fixture service
uses deterministic AnnData-like inputs; production deployment should replace
the fixture reader with controlled `scanpy.read_h5ad` storage access.
