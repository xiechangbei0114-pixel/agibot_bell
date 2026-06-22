#!/usr/bin/env python3
"""
☁️ 云端 VLA 桥接器 — WebSocket 版

当你租了 AutoDL 云 GPU 后，用这个脚本替代 simulate_vla.py。
它通过 WebSocket 连接到云端推理服务器，获取 VLA 结果后发到 ROS2。

工作流程：
  云端: VLA 模型 (Pi0/OpenVLA) → WebSocket Server
    ↑                               ↓
  本地: 订阅 /parts_detected → WebSocket Client → 发布 /vla_pose

用法：
  # 1. 在 AutoDL 上部署推理服务器（见 deploy_to_autodl.md）
  # 2. 本地运行：
  python3 cloud_vla_bridge/vla_cloud_bridge.py --ws ws://你的服务器IP:8765
  
  # 3. 效果跟 simulate_vla.py 一样，但推理是真的 VLA 模型在跑
"""

import rclpy
import json
import argparse
import asyncio
import threading
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False


class VLACloudBridge(Node):
    """
    云端 VLA 桥接器：
      收到来料 → 通过 WebSocket 发到云端推理 → 收到结果 → 发布位姿
    """

    def __init__(self, ws_url):
        super().__init__('vla_cloud_bridge')
        self.ws_url = ws_url
        
        # ROS2 通信
        self.sub = self.create_subscription(
            String, 'parts_detected', self.on_part, 10
        )
        self.pose_pub = self.create_publisher(PoseStamped, 'vla_pose', 10)
        self.log_pub = self.create_publisher(String, 'vla_inference_log', 10)
        
        # WebSocket 连接池
        self.ws_connection = None
        self.loop = None
        self.pending_requests = {}
        
        # 启动异步事件循环线程
        self.ws_thread = threading.Thread(target=self._run_ws_loop, daemon=True)
        self.ws_thread.start()
        
        self.get_logger().info(f'☁️ 云端 VLA 桥接器已启动')
        self.get_logger().info(f'   服务器: {ws_url}')
        self.get_logger().info(f'   等待来料信号...')

    def _run_ws_loop(self):
        """在后台线程中运行异步事件循环"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._ws_main())

    async def _ws_main(self):
        """WebSocket 主循环：保持连接"""
        while True:
            try:
                async with websockets.connect(self.ws_url) as ws:
                    self.ws_connection = ws
                    self.get_logger().info('✅ 已连接到云端推理服务器')
                    
                    # 保持心跳
                    async for message in ws:
                        await self._handle_cloud_response(message)
                        
            except Exception as e:
                self.get_logger().warn(f'🔄 连接断开，5秒后重试... ({e})')
                self.ws_connection = None
                await asyncio.sleep(5)

    async def _handle_cloud_response(self, message):
        """处理云端返回的推理结果"""
        try:
            data = json.loads(message)
            request_id = data.get('request_id')
            
            if request_id in self.pending_requests:
                part_info = self.pending_requests.pop(request_id)
                part_id = part_info['part_id']
                ptype = part_info['ptype']
                
                if data.get('status') == 'success':
                    pose = data['pose']
                    
                    # 发布位姿到 ROS2
                    pose_msg = PoseStamped()
                    pose_msg.header.frame_id = 'panda_link0'
                    pose_msg.header.stamp = self.get_clock().now().to_msg()
                    pose_msg.pose.position.x = pose['x']
                    pose_msg.pose.position.y = pose['y']
                    pose_msg.pose.position.z = pose['z']
                    pose_msg.pose.orientation.w = 1.0
                    
                    self.pose_pub.publish(pose_msg)
                    
                    log = String()
                    log.data = f'{part_id}|VLA_OK|{ptype}|云端推理位姿({pose["x"]:.3f},{pose["y"]:.3f})'
                    self.log_pub.publish(log)
                    
                    self.get_logger().info(f'✅ 云端推理完成 #{part_id}: ({pose["x"]:.3f}, {pose["y"]:.3f})')
                    
                else:
                    log = String()
                    log.data = f'{part_id}|VLA_FAIL|{ptype}|{data.get("error", "推理失败")}'
                    self.log_pub.publish(log)
                    self.get_logger().warn(f'❌ 云端推理失败 #{part_id}: {data.get("error")}')
                    
        except Exception as e:
            self.get_logger().error(f'处理云端响应失败: {e}')

    def on_part(self, msg):
        """收到来料 → 发送到云端推理"""
        if not self.ws_connection:
            self.get_logger().warn('⚠️ 未连接到云端服务器，跳过推理')
            return
        
        part_id, ptype, dx, dy = msg.data.split('|')
        
        # 构造推理请求
        import uuid
        request_id = str(uuid.uuid4())
        
        request = {
            'request_id': request_id,
            'type': 'vla_inference',
            'part_id': part_id,
            'part_type': ptype,
            'camera_image': None,  # 真实部署时传图片
            'prompt': f'抓取传送带上的{ptype}工件'
        }
        
        # 存待处理请求
        self.pending_requests[request_id] = {
            'part_id': part_id,
            'ptype': ptype
        }
        
        # 通过 WebSocket 发送
        asyncio.run_coroutine_threadsafe(
            self.ws_connection.send(json.dumps(request)),
            self.loop
        )
        
        self.get_logger().info(f'📤 发送推理请求 #{part_id} {ptype}')


def main():
    parser = argparse.ArgumentParser(description='云端 VLA 桥接器')
    parser.add_argument(
        '--ws', 
        type=str, 
        default='ws://localhost:8765',
        help='云端推理服务器的 WebSocket 地址'
    )
    args = parser.parse_args()
    
    if not HAS_WEBSOCKETS:
        print('❌ 请先安装 websockets: pip install websockets')
        return
    
    rclpy.init()
    node = VLACloudBridge(args.ws)
    
    print()
    print('=' * 55)
    print('  ☁️ 云端 VLA 桥接器')
    print(f'  服务器: {args.ws}')
    print('  订阅: /parts_detected')
    print('  发布: /vla_pose')
    print('=' * 55)
    print()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('\n🛑 桥接器停止')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
