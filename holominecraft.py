#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import math
import time
import ctypes
import socket
import urllib.request
from threading import Event, Thread
from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler, HTTPServer
try:
	import mss
except:
	print('Install mss with "pip3 install mss"')
	quit()
try:
	import cv2
	import numpy as np
except:
	print('Install OpenCV with "pip3 install opencv-python"')
	quit()
try:
	import win32api
	import win32gui
	from win32con import MONITOR_DEFAULTTONEAREST
except:
	print('Install pywin32 with "pip3 install pywin32"')
	quit()
try:
	from diff_match_patch import diff_match_patch
except:
	print('Install diff-match-patch with "pip3 install diff-match-patch"')
	quit()

ip = socket.gethostbyname(socket.gethostname())
port = 9090
x, y, w, h = 0, 0, 0, 0
fps = 15

with urllib.request.urlopen('https://cdn.jsdelivr.net/npm/holoplay@0.2.3/holoplay.js') as f:
	holoplay_js_vanilla = f.read().decode('utf-8')

with urllib.request.urlopen('https://raw.githubusercontent.com/jankais3r/driverless-HoloPlay.js/main/holoplay.js.patch') as f:
	diff = f.read().decode('utf-8').replace('\r\n', '\n')
	dmp = diff_match_patch()
	patches = dmp.patch_fromText(diff)
	holoplay_js, _ = dmp.patch_apply(patches, holoplay_js_vanilla)
	holoplay_js = holoplay_js.replace('localhost', ip)
	holoplay_js = holoplay_js.replace(
	# Original calibration:
	'{"configVersion":"1.0","serial":"00000","pitch":{"value":49.825218200683597},"slope":{"value":5.2160325050354},"center":{"value":-0.23396748304367066},"viewCone":{"value":40.0},"invView":{"value":1.0},"verticalAngle":{"value":0.0},"DPI":{"value":338.0},"screenW":{"value":2560.0},"screenH":{"value":1600.0},"flipImageX":{"value":0.0},"flipImageY":{"value":0.0},"flipSubp":{"value":0.0}}',
	# Your calibration:
	'{"configVersion":"1.0","serial":"00000","pitch":{"value":47.56401443481445},"slope":{"value":-5.480000019073486},"center":{"value":0.374184787273407},"viewCone":{"value":40.0},"invView":{"value":1.0},"verticalAngle":{"value":0.0},"DPI":{"value":338.0},"screenW":{"value":2560.0},"screenH":{"value":1600.0},"flipImageX":{"value":0.0},"flipImageY":{"value":0.0},"flipSubp":{"value":0.0}}')

class CamHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		global ip, port
		jpegQuality = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
		if self.path.endswith('/rgb.mjpg'):
			self.send_response(200)
			self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()
			while True:
				if(rgbframe.any() != None):
					pass
				r, buf = cv2.imencode('.jpg', rgbframe, jpegQuality)
				try:
					self.wfile.write('--jpgboundary\r\n'.encode())
					self.end_headers()
					self.wfile.write(bytearray(buf))
				except:
					pass
			return
		
		if self.path.endswith('/depth.mjpg'):
			self.send_response(200)
			self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
			self.send_header('Access-Control-Allow-Origin', '*')
			self.end_headers()
			while True:
				if(depthframe.any() != None):
					pass
				r, buf = cv2.imencode('.jpg', depthframe, jpegQuality)
				try:
					self.wfile.write('--jpgboundary\r\n'.encode())
					self.end_headers()
					self.wfile.write(bytearray(buf))
				except:
					pass
			return
		
		if self.path.endswith('holoplay.js'):
			self.send_response(200)
			self.send_header('Content-type', 'text/javascript')
			self.end_headers()
			self.wfile.write((holoplay_js).encode())
			return
		
		if self.path.endswith('holo.html'):
			texture = 'rgb'
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			skip = 2
			size = 6
			depthspread = 1300
			self.wfile.write(('''<!DOCTYPE html>
			<html>
			<head>
			<meta charset="utf-8"/>
				<style>
				body {
					margin: 0;
					cursor: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAFiUAABYlAUlSJPAAAAAMSURBVBhXY/j//z8ABf4C/qc1gYQAAAAASUVORK5CYII=), auto;);
				}
				
				canvas {
					width: 100vw;
					height: 100vh;
					display: block;
				}
				</style>
			</head>

			<body>
				<script src="https://cdn.jsdelivr.net/npm/three@0.121.1/build/three.min.js"></script>
				<script src="http://''' + ip + ':' + str(port) + '''/holoplay.js"></script>
				<script>
					/* global THREE */
					function loadImage(url) {
						return new Promise((resolve, reject) => {
							var img = new Image();
							img.crossOrigin = "anonymous";
							img.onload = (e) => {
								resolve(img);
							};
							img.onerror = reject;
							img.src = url;
						});
					}

					function getImageData(img) {
						var ctx = document.createElement("canvas").getContext("2d");
						ctx.canvas.width = img.width;
						ctx.canvas.height = img.height;
						ctx.drawImage(img, 0, 0);
						return ctx.getImageData(0, 0, ctx.canvas.width, ctx.canvas.height);
					}
					// return the pixel at UV coordinates (0 to 1) in 0 to 1 values
					function getPixel(imageData, u, v) {
						var x = u * (imageData.width - 1) | 0;
						var y = v * (imageData.height - 1) | 0;
						if(x < 0 || x >= imageData.width || y < 0 || y >= imageData.height) {
							return [0, 0, 0, 0];
						} else {
							var offset = (y * imageData.width + x) * 4;
							return Array.from(imageData.data.slice(offset, offset + 4)).map(v => v / 255);
						}
					}
					async function main() {
						var images = await Promise.all([
							loadImage("http://''' + ip + ':' + str(port) + '''/''' + texture + '''.mjpg"),
							loadImage("http://''' + ip + ':' + str(port) + '''/depth.mjpg")
						]);
						var data = images.map(getImageData);
						var canvas = document.querySelector("canvas");
						var renderer = new THREE.WebGLRenderer();
						document.body.appendChild(renderer.domElement);
						var fov = 72; // iPhone Facetime camera FOV
						var aspect = 2;
						var near = 1;
						var far = 4500;
						var size = ''' + str(size) + '''; // size of points - decrease for more "pointy cloudy" feel
						var camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
						camera.position.z = 2500;
						var scene = new THREE.Scene();
						var holoplay = new HoloPlay(scene, camera, renderer);
						var rgbData = data[0];
						var depthData = data[1];
						var skip = ''' + str(skip) + '''; // space between points - increase for better FPS
						var across = Math.ceil(rgbData.width / skip);
						var down = Math.ceil(rgbData.height / skip);
						var positions = [];
						var colors = [];
						var spread = 900;
						var depthSpread = ''' + str(depthspread) + ''';
						var imageAspect = 1.67; //rgbData.width / rgbData.height
						for(let y = 0; y < down; ++y) {
							var v = y / (down - 1);
							for(let x = 0; x < across; ++x) {
								var u = x / (across - 1);
								var rgb = getPixel(rgbData, u, v);
								var depth = 1 - getPixel(depthData, u, v)[0];
								positions.push((u * 2 - 1) * spread * imageAspect, (v * -2 + 1) * spread, depth * depthSpread);
								colors.push(...rgb.slice(0, 3));
							}
						}
						var geometry = new THREE.BufferGeometry();
						geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
						geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
						geometry.computeBoundingSphere();
						var material = new THREE.PointsMaterial({
							size: size,
							vertexColors: THREE.VertexColors
						});
						var points = new THREE.Points(geometry, material);
						points.name = "hologram";
						scene.add(points);
						setInterval(function() {
							refresh()
						}, ''' + str(1000 / fps) + ''')
						
						async function refresh() {
							data = images.map(getImageData);
							rgbData = data[0];
							depthData = data[1];
							positions = [];
							colors = [];
							for(let y = 0; y < down; ++y) {
								v = y / (down - 1);
								for(let x = 0; x < across; ++x) {
									u = x / (across - 1);
									rgb = getPixel(rgbData, u, v);
									depth = 1 - getPixel(depthData, u, v)[0];
									positions.push((u * 2 - 1) * spread * imageAspect, (v * -2 + 1) * spread, depth * depthSpread);
									colors.push(...rgb.slice(0, 3));
								}
							}
							geometry = new THREE.BufferGeometry();
							geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
							geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
							geometry.computeBoundingSphere();
							material = new THREE.PointsMaterial({
								size: size,
								vertexColors: THREE.VertexColors
							});
							
							var oldObject = scene.getObjectByName("hologram")
							scene.remove(oldObject);
							oldObject.geometry.dispose();
							oldObject.material.dispose();
							oldObject = undefined;
							
							points = new THREE.Points(geometry, material);
							points.name = "hologram";
							scene.add(points);
						}
						
						function resizeRendererToDisplaySize(renderer) {
							var canvas = renderer.domElement;
							var width = canvas.clientWidth;
							var height = canvas.clientHeight;
							var needResize = canvas.width !== width || canvas.height !== height;
							if(needResize) {
								renderer.setSize(width, height, false);
							}
							return needResize;
						}

						function render(time) {
							time *= 0.001;
							if(resizeRendererToDisplaySize(renderer)) {
								var canvas = renderer.domElement;
								camera.aspect = canvas.clientWidth / canvas.clientHeight;
								camera.updateProjectionMatrix();
							}
							holoplay.render(scene, camera);
							requestAnimationFrame(render);
						}
						requestAnimationFrame(render);
					}
					main();
				</script>
				<button onclick="openFullscreen();" style="position: absolute">Fullscreen</button>
				<script>
					var elem = document.documentElement;
					var btn = document.getElementsByTagName('button')[0];
					function openFullscreen() {
						if (elem.requestFullscreen) {
							elem.requestFullscreen();
						} else if (elem.webkitRequestFullscreen) { /* Safari */
							elem.webkitRequestFullscreen();
						}
						btn.parentNode.removeChild(btn);
					}
				</script>
			</body>
			</html>''').encode())
			return
		
		if self.path == '/':
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write('<html><head></head><body>'.encode())
			self.wfile.write(('<img src="http://' + ip + ':' + str(port) + '/rgb.mjpg" style="max-height: 45%"/>').encode())
			self.wfile.write(('<br><img src="http://' + ip + ':' + str(port) + '/depth.mjpg" style="max-height: 45%"/>').encode())
			self.wfile.write(('<br><a href="http://' + ip + ':' + str(port) + '/holo.html">Open HoloMinecraft</a>').encode())
			self.wfile.write('</body></html>'.encode())
			return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def callback(hwnd, extra):
	global x, y, w, h
	if win32gui.GetWindowText(hwnd)[:9] == 'Minecraft':
		shcore = ctypes.windll.shcore
		shcore.SetProcessDpiAwareness(2)
		monitor = win32api.MonitorFromWindow(hwnd)
		dpiX = ctypes.c_uint()
		dpiY = ctypes.c_uint()
		shcore.GetDpiForMonitor(
			monitor.handle,
			0,
			ctypes.byref(dpiX),
			ctypes.byref(dpiY)
		)
		scaling = dpiX.value / 96
		
		rect = win32gui.GetWindowRect(hwnd)
		x = rect[0] + math.floor(8 * scaling)
		y = rect[1] + math.floor(31 * scaling)
		w = rect[2] - x - math.floor(8 * scaling)
		h = rect[3] - y - math.floor(8 * scaling)
		print('Found "%s" ' % win32gui.GetWindowText(hwnd) + 'window of size (%d,%d) ' % (w, h) + 'in location (%d,%d).' % (x, y))

def main():
	global rgbframe, depthframe
	server = ThreadedHTTPServer(('0.0.0.0', port), CamHandler)
	print('Starting server on address ' + ip + ':' + str(port))
	target = Thread(target = server.serve_forever, args = ())
	target.start()
	mon = {'top': y, 'left': x, 'width': w, 'height': h}
	sct = mss.mss()
	
	while True:
		start = time.time()
		img = np.asarray(sct.grab(mon))
		if((img[0,0][0] == img[0,0][1] == img[0,0][2]) and (img[50,50][0] == img[50,50][1] == img[50,50][2])):
			depthframe = img
		else:
			rgbframe = img
		
		time.sleep(1 / (fps * 2))
		#cv2.imshow('Depthmap', depthframe)
		#cv2.imshow('RGB', rgbframe)
		#if cv2.waitKey(25) & 0xFF == ord("q"):
		#	cv2.destroyAllWindows()
		#	break

win32gui.EnumWindows(callback, None)
if(x ==0 and y == 0 and w == 0 and h == 0):
	print('No Minecraft window found.')
	quit()
rgbframe = np.zeros([w, h, 3], dtype = np.uint8)
rgbframe.fill(0)
depthframe = np.zeros([w, h, 3], dtype = np.uint8)
depthframe.fill(0)
main()
