import asyncio, tempfile, os, shutil

async def test():
    tmp = tempfile.mkdtemp()
    pdf_src = r'C:\contract-review-system\test\(佛光)合約管理系統維護合約書_V1.0_20260309.docx.pdf'
    shutil.copy(pdf_src, os.path.join(tmp, 'input.pdf'))

    mount = tmp.replace('\\', '/')
    if len(mount) >= 2 and mount[1] == ':':
        mount = '/' + mount[0].lower() + mount[2:]
    print('mount path:', mount)

    proc = await asyncio.create_subprocess_exec(
        'docker', 'run', '--rm',
        '-v', mount + ':/pdf',
        '--entrypoint', 'sh',
        'iapain/pdf2htmlex',
        '-c', 'cd /pdf && pdf2htmlEX --zoom 1.3 input.pdf output.html',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, err = await asyncio.wait_for(proc.communicate(), timeout=120)
    out_path = os.path.join(tmp, 'output.html')
    print('returncode:', proc.returncode)
    print('html exists:', os.path.exists(out_path))
    if os.path.exists(out_path):
        print('html size:', os.path.getsize(out_path), 'bytes')
    shutil.rmtree(tmp, ignore_errors=True)
    print('done')

asyncio.run(test())
