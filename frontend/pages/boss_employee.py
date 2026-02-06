import streamlit as st
import requests
import threading
import queue
import time
from services.api_client import call_rag_api, FASTAPI_URL   # later separate endpoint

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}

def render():
    st.header("🏢 Boss–Employee Agent System")

    task = st.text_input("Enter task for Boss Agent")

    if "boss_answer" not in st.session_state:
        st.session_state.boss_answer = None
    if "boss_logs" not in st.session_state:
        st.session_state.boss_logs = []
    if "boss_running" not in st.session_state:
        st.session_state.boss_running = False

    if st.button("Run Multi-Agent System"):
        if not task:
            st.warning("Please enter a task")
            return

        st.session_state.boss_answer = None
        st.session_state.boss_logs = []
        st.session_state.boss_running = True

        log_queue: "queue.Queue[str]" = queue.Queue()
        log_stop = threading.Event()
        result_holder = {"data": None, "error": None}

        def logs_worker():
            url = f"{FASTAPI_URL}/logs/stream"
            try:
                with requests.get(url, stream=True, timeout=60) as resp:
                    resp.raise_for_status()
                    for raw in resp.iter_lines(decode_unicode=True):
                        if log_stop.is_set():
                            break
                        if not raw:
                            continue
                        if raw.startswith("data: "):
                            log_queue.put(raw[6:])
                        elif raw.startswith("event: end"):
                            break
            except Exception:
                pass

        def chat_worker():
            try:
                result_holder["data"] = call_rag_api(task)   # 🔴 temp reuse
            except Exception as exc:
                result_holder["error"] = exc
            finally:
                log_stop.set()

        log_thread = threading.Thread(target=logs_worker, daemon=True)
        chat_thread = threading.Thread(target=chat_worker, daemon=True)
        log_thread.start()
        chat_thread.start()

        log_container = st.container(height=200)
        log_display = log_container.empty()

        with st.spinner("Agents working..."):
            while chat_thread.is_alive():
                while True:
                    try:
                        line = log_queue.get_nowait()
                        st.session_state.boss_logs.append(line)
                    except queue.Empty:
                        break

                log_text = "\n".join(st.session_state.boss_logs[-500:])
                log_display.code(log_text)
                time.sleep(0.2)

        chat_thread.join()
        log_stop.set()
        log_thread.join(timeout=1.0)

        while True:
            try:
                line = log_queue.get_nowait()
                st.session_state.boss_logs.append(line)
            except queue.Empty:
                break

        log_text = "\n".join(st.session_state.boss_logs[-500:])
        log_display.code(log_text)

        if result_holder["error"] is not None:
            st.error(f"API error: {result_holder['error']}")
            st.session_state.boss_answer = None
        else:
            st.session_state.boss_answer = result_holder["data"]

        st.session_state.boss_running = False

    if st.session_state.boss_answer is not None:
        st.success("Final Output")
        result = st.session_state.boss_answer
        summary = result.get("summary")
        if summary is None:
            summary = result.get("response", result)
        st.write(summary)

        artifacts = result.get("artifacts") or []
        if artifacts:
            with st.sidebar:
                st.subheader("Artifacts")
                for artifact in artifacts:
                    filename = artifact.get("filename")
                    filetype = (artifact.get("filetype") or "").lower()
                    if not filename:
                        continue

                    url = f"{FASTAPI_URL}/outputs/{filename}"

                    if filetype in IMAGE_EXTS:
                        st.image(url, caption=filename, use_container_width=True)
                    elif filetype == ".py":
                        try:
                            resp = requests.get(url, timeout=30)
                            resp.raise_for_status()
                            st.code(resp.text, language="python")
                        except Exception as exc:
                            st.warning(f"Could not load {filename}: {exc}")
                    elif filetype == ".csv":
                        try:
                            resp = requests.get(url, timeout=30)
                            resp.raise_for_status()
                            st.download_button(
                                label=f"Download {filename}",
                                data=resp.content,
                                file_name=filename,
                                mime="text/csv",
                            )
                        except Exception as exc:
                            st.warning(f"Could not load {filename}: {exc}")
                    else:
                        try:
                            resp = requests.get(url, timeout=30)
                            resp.raise_for_status()
                            st.download_button(
                                label=f"Download {filename}",
                                data=resp.content,
                                file_name=filename,
                            )
                        except Exception as exc:
                            st.warning(f"Could not load {filename}: {exc}")
