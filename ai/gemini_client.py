"""
Gemini API 客戶端

提供與 Google Gemini 的 AI 整合功能
"""
import sys
from pathlib import Path
import google.generativeai as genai
from typing import List, Dict, Optional
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import API_KEYS
from loguru import logger


class GeminiClient:
    """Gemini AI 客戶端"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Gemini 客戶端
        
        Args:
            api_key: Gemini API Key（若不提供則從設定檔讀取）
        """
        self.api_key = api_key or API_KEYS.get('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("未設定 GEMINI_API_KEY")
        
        # 配置 Gemini
        genai.configure(api_key=self.api_key)
        
        # 使用 Gemini 2.5 Pro（規格書指定）
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        logger.info("Gemini 客戶端初始化成功")
    
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 8000,
        retry_count: int = 3
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 提示詞
            temperature: 溫度參數（0-1，越高越創意）
            max_tokens: 最大 token 數
            retry_count: 重試次數
        
        Returns:
            生成的文本
        """
        for attempt in range(retry_count):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                )
                
                if response.text:
                    logger.success("Gemini 生成成功")
                    return response.text
                else:
                    logger.warning("Gemini 返回空內容")
                    return ""
                
            except Exception as e:
                logger.error(f"Gemini API 錯誤（嘗試 {attempt+1}/{retry_count}）: {e}")
                
                if attempt < retry_count - 1:
                    # 指數退避
                    wait_time = 2 ** attempt
                    logger.info(f"等待 {wait_time} 秒後重試...")
                    time.sleep(wait_time)
                else:
                    logger.error("Gemini API 請求失敗，已達最大重試次數")
                    raise
        
        return ""
    
    def generate_with_context(
        self,
        prompt: str,
        context_data: Dict,
        template_name: str = "default"
    ) -> str:
        """
        基於上下文資料生成文本
        
        Args:
            prompt: 基礎提示詞
            context_data: 上下文資料字典
            template_name: 模板名稱
        
        Returns:
            生成的文本
        """
        # 構建完整提示詞
        full_prompt = self._build_prompt(prompt, context_data, template_name)
        
        return self.generate_text(full_prompt)
    
    def _build_prompt(
        self,
        base_prompt: str,
        context: Dict,
        template: str
    ) -> str:
        """
        構建完整提示詞
        
        Args:
            base_prompt: 基礎提示
            context: 上下文資料
            template: 模板名稱
        
        Returns:
            完整提示詞
        """
        # 格式化上下文資料
        context_str = "\n".join([
            f"{key}: {value}"
            for key, value in context.items()
        ])
        
        full_prompt = f"""
{base_prompt}

=== 資料上下文 ===
{context_str}

=== 指令 ===
請根據以上資料進行專業分析，使用繁體中文回答。
分析應該：
1. 客觀且基於數據
2. 提供具體的投資建議
3. 說明風險與機會
4. 使用 Markdown 格式
"""
        
        return full_prompt
    
    def batch_generate(
        self,
        prompts: List[str],
        delay: float = 1.0
    ) -> List[str]:
        """
        批次生成（避免超過 API 限流）
        
        Args:
            prompts: 提示詞列表
            delay: 每次請求間隔（秒）
        
        Returns:
            生成結果列表
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            logger.info(f"批次生成 {i+1}/{len(prompts)}")
            
            result = self.generate_text(prompt)
            results.append(result)
            
            # 避免超過限流
            if i < len(prompts) - 1:
                time.sleep(delay)
        
        return results


# 測試
if __name__ == '__main__':
    try:
        client = GeminiClient()
        
        # 簡單測試
        prompt = "請用一段話說明什麼是量化投資"
        response = client.generate_text(prompt, temperature=0.7)
        
        print("=" * 60)
        print("Gemini 測試結果：")
        print("=" * 60)
        print(response)
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"測試失敗：{e}")
