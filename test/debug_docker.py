import asyncio, tempfile, os, shutil

async def test():
    tmp = tempfile.mkdtemp()
    print('tmp_dir:', tmp)
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
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
        print('returncode:', proc.returncode)
        print('stdout:', stdout.decode())
        print('stderr:', stderr.decode()[:500])
    except asyncio.TimeoutError:
        print('TIMEOUT after 120s')
        proc.kill()

    out = os.path.join(tmp, 'output.html')
    print('output exists:', os.path.exists(out))
    if os.path.exists(out):
        print('output size:', os.path.getsize(out))
    shutil.rmtree(tmp, ignore_errors=True)

asyncio.run(test())
