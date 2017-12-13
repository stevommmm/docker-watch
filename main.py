import asyncio
import aiodocker
import json
from aiohttp import web
import logging
import os


logger = logging.getLogger('Watch')
logger.setLevel(logging.INFO)


async def handle_ws(request):
	resp = web.WebSocketResponse(heartbeat=30)
	await resp.prepare(request)

	try:
		request.app['sockets'].append(resp)
		async for msg in resp:
			print(msg)
		return resp
	finally:
		request.app['sockets'].remove(resp)


async def handle_index(request):
	return web.FileResponse('static/index.html')

async def on_shutdown(app):
	for ws in app['sockets']:
		await ws.close()


async def listen_events(app):
		try:
			sub = app['docker'].events.subscribe()
			while True:
				msg = await sub.get()
				if 'time' in msg:
					msg['time'] = msg['time'].timestamp()
				for ws in app['sockets']:
					ws.send_str(json.dumps(msg))
		except asyncio.CancelledError:
			pass


async def start_background_tasks(app):
	app['docker'] = aiodocker.Docker()
	app['listener'] = app.loop.create_task(listen_events(app))


async def cleanup_background_tasks(app):
	app['listener'].cancel()
	await app['listener']


if __name__ == '__main__':
	loop = asyncio.get_event_loop()

	app = web.Application(loop=loop)
	app['sockets'] = []

	app.on_startup.append(start_background_tasks)
	app.on_cleanup.append(cleanup_background_tasks)
	app.on_shutdown.append(on_shutdown)

	app.router.add_get('/', handle_index)
	app.router.add_get('/ws', handle_ws)
	web.run_app(app)
