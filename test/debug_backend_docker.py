"""模擬後端的 extract_html_from_pdf，看哪個步驟失敗"""
import asyncio, tempfile, os, shutil, logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

async def extract_html_from_pdf(file_bytes: bytes) -> str:
    tmp_dir = tempfile.mkdtemp(dir=r"C:\contract-review-system\tmp")
    logger.info(f"tmp_dir: {tmp_dir}")
    try:
        pdf_path = os.path.join(tmp_dir, "input.pdf")
        html_path = os.path.join(tmp_dir, "output.html")

        with open(pdf_path, "wb") as f:
            f.write(file_bytes)
        logger.info(f"PDF written: {pdf_path}")

        mount = tmp_dir.replace("\\", "/")
        if len(mount) >= 2 and mount[1] == ":":
            mount = "/" + mount[0].lower() + mount[2:]
        logger.info(f"mount: {mount}")

        proc = await asyncio.create_subprocess_exec(
            "docker", "run", "--rm",
            "-v", mount + ":/pdf",
            "--entrypoint", "sh",
            "iapain/pdf2htmlex",
            "-c", "cd /pdf && pdf2htmlEX --zoom 1.3 input.pdf output.html",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        logger.info("Docker process started")
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
        logger.info(f"returncode: {proc.returncode}")
        logger.info(f"stderr: {stderr.decode()[:300]}")

        if proc.returncode != 0:
            logger.error("Docker returned non-zero")
            return ""

        logger.info(f"html_path exists: {os.path.exists(html_path)}")
        if not os.path.exists(html_path):
            return ""

        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        logger.info(f"HTML size: {len(html)}")
        return html

    except asyncio.TimeoutError:
        logger.error("TIMEOUT")
        return ""
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)
        return ""
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

async def main():
    with open(r"C:\contract-review-system\test\(佛光)合約管理系統維護合約書_V1.0_20260309.docx.pdf", "rb") as f:
        data = f.read()
    html = await extract_html_from_pdf(data)
    print(f"\n=== RESULT: htmlContent size = {len(html)} ===")

asyncio.run(main())
