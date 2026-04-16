"""
知识库管理接口测试
"""

import pytest
import json


class TestKnowledgeBaseEndpoints:
    """知识库管理端点测试类"""
    
    def test_list_knowledge_bases_success(self, client, auth_headers):
        """测试获取知识库列表成功"""
        response = client.get('/api/v1/cs/knowledge/',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    def test_list_knowledge_bases_without_auth(self, client):
        """测试未认证获取知识库列表"""
        response = client.get('/api/v1/cs/knowledge/')
        
        assert response.status_code == 401
    
    def test_create_knowledge_base_success(self, client, auth_headers, test_data):
        """测试创建知识库成功"""
        kb_data = test_data.create_test_knowledge_base()
        
        response = client.post('/api/v1/cs/knowledge/',
                              data=json.dumps(kb_data),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'data' in data
        assert data['data']['name'] == kb_data['name']
        assert 'id' in data['data']
        assert 'created_at' in data['data']
    
    def test_create_knowledge_base_missing_name(self, client, auth_headers):
        """测试创建知识库缺少名称"""
        kb_data = {
            'description': '没有名称的知识库'
        }
        
        response = client.post('/api/v1/cs/knowledge/',
                              data=json.dumps(kb_data),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_knowledge_base_empty_body(self, client, auth_headers):
        """测试创建知识库空请求体"""
        response = client.post('/api/v1/cs/knowledge/',
                              data=json.dumps({}),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 400
    
    def test_get_knowledge_base_success(self, client, auth_headers, test_data):
        """测试获取知识库详情成功"""
        # 先创建知识库
        kb_data = test_data.create_test_knowledge_base()
        create_response = client.post('/api/v1/cs/knowledge/',
                                     data=json.dumps(kb_data),
                                     content_type='application/json',
                                     headers=auth_headers)
        
        kb_id = create_response.get_json()['data']['id']
        
        # 获取详情
        response = client.get(f'/api/v1/cs/knowledge/{kb_id}',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['id'] == kb_id
    
    def test_get_knowledge_base_not_found(self, client, auth_headers):
        """测试获取不存在的知识库"""
        response = client.get('/api/v1/cs/knowledge/kb_nonexistent',
                             headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_update_knowledge_base_success(self, client, auth_headers, test_data):
        """测试更新知识库成功"""
        # 先创建知识库
        kb_data = test_data.create_test_knowledge_base()
        create_response = client.post('/api/v1/cs/knowledge/',
                                     data=json.dumps(kb_data),
                                     content_type='application/json',
                                     headers=auth_headers)
        
        kb_id = create_response.get_json()['data']['id']
        
        # 更新
        update_data = {
            'name': '更新后的知识库名称',
            'description': '更新后的描述'
        }
        response = client.put(f'/api/v1/cs/knowledge/{kb_id}',
                             data=json.dumps(update_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['name'] == update_data['name']
    
    def test_update_knowledge_base_not_found(self, client, auth_headers):
        """测试更新不存在的知识库"""
        update_data = {'name': '新名称'}
        response = client.put('/api/v1/cs/knowledge/kb_nonexistent',
                             data=json.dumps(update_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_delete_knowledge_base_success(self, client, auth_headers, test_data):
        """测试删除知识库成功"""
        # 先创建知识库
        kb_data = test_data.create_test_knowledge_base()
        create_response = client.post('/api/v1/cs/knowledge/',
                                     data=json.dumps(kb_data),
                                     content_type='application/json',
                                     headers=auth_headers)
        
        kb_id = create_response.get_json()['data']['id']
        
        # 删除
        response = client.delete(f'/api/v1/cs/knowledge/{kb_id}',
                                headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['deleted'] is True


class TestDocumentEndpoints:
    """文档管理端点测试类"""
    
    def test_list_documents_success(self, client, auth_headers, test_data):
        """测试获取文档列表成功"""
        # 先创建知识库
        kb_data = test_data.create_test_knowledge_base()
        create_response = client.post('/api/v1/cs/knowledge/',
                                     data=json.dumps(kb_data),
                                     content_type='application/json',
                                     headers=auth_headers)
        
        kb_id = create_response.get_json()['data']['id']
        
        response = client.get(f'/api/v1/cs/knowledge/{kb_id}/docs',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data['data']
    
    def test_create_document_success(self, client, auth_headers, test_data):
        """测试创建文档成功"""
        # 先创建知识库
        kb_data = test_data.create_test_knowledge_base()
        create_response = client.post('/api/v1/cs/knowledge/',
                                     data=json.dumps(kb_data),
                                     content_type='application/json',
                                     headers=auth_headers)
        
        kb_id = create_response.get_json()['data']['id']
        
        # 创建文档
        doc_data = test_data.create_test_document()
        response = client.post(f'/api/v1/cs/knowledge/{kb_id}/docs',
                              data=json.dumps(doc_data),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['data']['title'] == doc_data['title']
        assert data['data']['kb_id'] == kb_id
    
    def test_create_document_missing_title(self, client, auth_headers, test_data):
        """测试创建文档缺少标题"""
        # 先创建知识库
        kb_data = test_data.create_test_knowledge_base()
        create_response = client.post('/api/v1/cs/knowledge/',
                                     data=json.dumps(kb_data),
                                     content_type='application/json',
                                     headers=auth_headers)
        
        kb_id = create_response.get_json()['data']['id']
        
        doc_data = {'content': '没有标题的文档'}
        response = client.post(f'/api/v1/cs/knowledge/{kb_id}/docs',
                              data=json.dumps(doc_data),
                              content_type='application/json',
                              headers=auth_headers)
        
        assert response.status_code == 400
    
    def test_update_document_success(self, client, auth_headers, test_data):
        """测试更新文档成功"""
        # 先创建知识库和文档
        kb_data = test_data.create_test_knowledge_base()
        kb_response = client.post('/api/v1/cs/knowledge/',
                                 data=json.dumps(kb_data),
                                 content_type='application/json',
                                 headers=auth_headers)
        kb_id = kb_response.get_json()['data']['id']
        
        doc_data = test_data.create_test_document()
        doc_response = client.post(f'/api/v1/cs/knowledge/{kb_id}/docs',
                                  data=json.dumps(doc_data),
                                  content_type='application/json',
                                  headers=auth_headers)
        doc_id = doc_response.get_json()['data']['id']
        
        # 更新文档
        update_data = {'title': '更新后的文档标题'}
        response = client.put(f'/api/v1/cs/knowledge/{kb_id}/docs/{doc_id}',
                             data=json.dumps(update_data),
                             content_type='application/json',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['title'] == update_data['title']
    
    def test_delete_document_success(self, client, auth_headers, test_data):
        """测试删除文档成功"""
        # 先创建知识库和文档
        kb_data = test_data.create_test_knowledge_base()
        kb_response = client.post('/api/v1/cs/knowledge/',
                                 data=json.dumps(kb_data),
                                 content_type='application/json',
                                 headers=auth_headers)
        kb_id = kb_response.get_json()['data']['id']
        
        doc_data = test_data.create_test_document()
        doc_response = client.post(f'/api/v1/cs/knowledge/{kb_id}/docs',
                                  data=json.dumps(doc_data),
                                  content_type='application/json',
                                  headers=auth_headers)
        doc_id = doc_response.get_json()['data']['id']
        
        # 删除文档
        response = client.delete(f'/api/v1/cs/knowledge/{kb_id}/docs/{doc_id}',
                                headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['deleted'] is True
    
    def test_search_documents(self, client, auth_headers, test_data):
        """测试搜索文档"""
        response = client.get('/api/v1/cs/knowledge/search?q=测试',
                             headers=auth_headers)
        
        # 搜索结果可能为空，但接口应该正常返回
        assert response.status_code in [200, 400]
