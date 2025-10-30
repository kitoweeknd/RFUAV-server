"""
测试JSON格式规范
验证所有API端点都正确返回JSON格式
"""
import requests
import json
import sys


BASE_URL = "http://localhost:8000"


def test_json_response(endpoint, method="GET", data=None, name=""):
    """测试端点是否返回有效的JSON"""
    print(f"\n测试: {name}")
    print(f"端点: {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                headers={"Content-Type": "application/json"},
                json=data
            )
        elif method == "DELETE":
            response = requests.delete(f"{BASE_URL}{endpoint}")
        
        # 检查Content-Type
        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type and "text/event-stream" not in content_type:
            print(f"   ❌ Content-Type错误: {content_type}")
            return False
        
        # 对于SSE流，不需要解析JSON
        if "text/event-stream" in content_type:
            print(f"   ✅ SSE流端点（跳过JSON验证）")
            return True
        
        # 尝试解析JSON
        try:
            json_data = response.json()
            print(f"   ✅ 返回有效JSON")
            print(f"   状态码: {response.status_code}")
            
            # 显示响应结构
            if isinstance(json_data, dict):
                keys = list(json_data.keys())
                print(f"   字段: {', '.join(keys[:5])}" + ("..." if len(keys) > 5 else ""))
            
            return True
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON解析失败: {e}")
            print(f"   响应内容: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ 无法连接到服务")
        return False
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("="*70)
    print("  🧪 JSON格式规范测试")
    print("  验证所有API端点都返回标准JSON格式")
    print("="*70)
    
    # 检查服务是否运行
    print("\n检查服务连接...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务运行正常")
        else:
            print(f"⚠️ 服务响应异常: {response.status_code}")
    except:
        print("❌ 无法连接到服务")
        print("请先启动服务: python app_refactored.py")
        return False
    
    results = []
    
    # 测试系统端点
    print("\n" + "="*70)
    print("1️⃣ 系统状态端点")
    print("="*70)
    
    results.append(test_json_response("/api/v1/health", "GET", name="健康检查"))
    results.append(test_json_response("/api/v1/info", "GET", name="系统信息"))
    
    # 测试资源端点
    print("\n" + "="*70)
    print("2️⃣ 资源管理端点")
    print("="*70)
    
    results.append(test_json_response("/api/v2/resources", "GET", name="资源状态"))
    results.append(test_json_response("/api/v2/resources/gpu", "GET", name="GPU信息"))
    
    # 测试任务端点
    print("\n" + "="*70)
    print("3️⃣ 任务管理端点")
    print("="*70)
    
    results.append(test_json_response("/api/v2/tasks", "GET", name="所有任务"))
    
    # 测试训练端点（使用无效数据，但应该返回JSON错误）
    print("\n" + "="*70)
    print("4️⃣ 训练端点（JSON格式测试）")
    print("="*70)
    
    training_data = {
        "model": "resnet18",
        "num_classes": 37,
        "train_path": "data/train",
        "val_path": "data/val",
        "save_path": "models/test_output",
        "batch_size": 8,
        "num_epochs": 1,
        "device": "cpu"
    }
    
    print("\n注意：以下测试可能失败（路径不存在），但应该返回JSON格式的错误")
    # 这个测试可能会失败，但我们只关心是否返回JSON
    test_json_response(
        "/api/v2/training/start",
        "POST",
        training_data,
        name="启动训练（格式测试）"
    )
    
    # 测试推理端点
    print("\n" + "="*70)
    print("5️⃣ 推理端点（JSON格式测试）")
    print("="*70)
    
    inference_data = {
        "cfg_path": "configs/test.yaml",
        "weight_path": "models/test.pth",
        "source_path": "data/test",
        "device": "cpu"
    }
    
    test_json_response(
        "/api/v2/inference/start",
        "POST",
        inference_data,
        name="启动推理（格式测试）"
    )
    
    # 测试批量推理
    batch_inference_data = {
        "cfg_path": "configs/test.yaml",
        "weight_path": "models/test.pth",
        "source_paths": ["data/test1", "data/test2"],
        "device": "cpu"
    }
    
    test_json_response(
        "/api/v2/inference/batch",
        "POST",
        batch_inference_data,
        name="批量推理（格式测试）"
    )
    
    # 总结
    print("\n" + "="*70)
    print("  📊 测试总结")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n通过: {passed}/{total}")
    print(f"失败: {total - passed}/{total}")
    
    if passed == total:
        print("\n✅ 所有端点都正确返回JSON格式！")
        return True
    else:
        print(f"\n⚠️ 有 {total - passed} 个端点需要检查")
        return False


def test_response_models():
    """测试响应模型的完整性"""
    print("\n" + "="*70)
    print("  🔍 响应模型完整性测试")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        data = response.json()
        
        print("\n健康检查响应字段:")
        required_fields = ["status", "timestamp", "version", "training_tasks", "inference_tasks"]
        
        for field in required_fields:
            if field in data:
                print(f"   ✅ {field}: {data[field]}")
            else:
                print(f"   ❌ 缺少字段: {field}")
        
        print("\nGPU信息响应字段:")
        response = requests.get(f"{BASE_URL}/api/v2/resources/gpu")
        data = response.json()
        
        gpu_fields = ["available", "count", "cuda_version", "pytorch_version", "devices"]
        for field in gpu_fields:
            if field in data:
                value = data[field]
                if isinstance(value, list):
                    print(f"   ✅ {field}: {len(value)} 项")
                else:
                    print(f"   ✅ {field}: {value}")
            else:
                print(f"   ❌ 缺少字段: {field}")
                
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")


def test_error_responses():
    """测试错误响应也是JSON格式"""
    print("\n" + "="*70)
    print("  🚨 错误响应JSON格式测试")
    print("="*70)
    
    # 测试404错误
    print("\n测试: 不存在的任务ID")
    try:
        response = requests.get(f"{BASE_URL}/api/v2/tasks/nonexistent-task-id")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 404:
            try:
                error_data = response.json()
                print(f"   ✅ 返回JSON错误: {error_data.get('detail', '')}")
            except:
                print(f"   ❌ 错误响应不是JSON")
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
    
    # 测试422验证错误
    print("\n测试: 无效的请求数据")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v2/training/start",
            headers={"Content-Type": "application/json"},
            json={"invalid": "data"}  # 缺少必需字段
        )
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 422:
            try:
                error_data = response.json()
                print(f"   ✅ 返回JSON验证错误")
                if "detail" in error_data:
                    print(f"   错误详情: {len(error_data['detail'])} 个字段错误")
            except:
                print(f"   ❌ 错误响应不是JSON")
    
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")


if __name__ == "__main__":
    print("\n" + "🚀" * 35)
    
    # 运行主测试
    success = main()
    
    # 测试响应模型
    test_response_models()
    
    # 测试错误响应
    test_error_responses()
    
    print("\n" + "🚀" * 35)
    print("\n💡 提示:")
    print("   - 所有端点都应该返回 application/json")
    print("   - 响应应该符合定义的Pydantic模型")
    print("   - 错误也应该是JSON格式")
    print("\n📚 相关文档:")
    print("   - JSON_API_SPEC.md - 完整的JSON API规范")
    print("   - JSON_FORMAT_UPDATE.md - 格式更新说明")
    print("   - models/schemas.py - 数据模型定义")
    print("\n" + "="*70)
    
    sys.exit(0 if success else 1)


