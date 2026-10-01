FROM python:3.12-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential cmake libopencv-dev nlohmann-json3-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY CMakeLists.txt ./
COPY Clip.cpp Clip.h VideoCompiler.cpp ./
COPY engine ./engine
# Build sequentially so compilation leaves memory available on t3.micro.
RUN cmake -S . -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build --parallel 1 && ctest --test-dir build --output-on-failure

FROM python:3.12-slim
# Do not pin the OpenCV runtime ABI package names: Debian updates them between
# slim base-image releases. The development meta-package keeps the deployment
# reliable while supplying the shared libraries used by video_engine.
RUN apt-get update && apt-get install -y --no-install-recommends libopencv-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --from=build /app/build/video_engine /app/build/video_engine
COPY api ./api
COPY mcp_server ./mcp_server
COPY django_admin ./django_admin
COPY flask_dashboard ./flask_dashboard
ENV PYTHONPATH=/app VIDEO_ENGINE_BIN=/app/build/video_engine DATA_DIR=/data
RUN mkdir -p /data
EXPOSE 8000
CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
