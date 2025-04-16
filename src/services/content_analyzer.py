from __future__ import annotations

import re
from typing import List
from logging import info, warning, debug
import json
import requests

class ContentAnalyzer:
    def __init__(self, folder_id: str, gpt_api_key: str):
        self.folder_id = folder_id
        self.gpt_api_key = gpt_api_key
        self.api_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {gpt_api_key}"
        }
        self.version_patterns = [
            r'v?\d+\.\d+(\.\d+)*(-\w+)?',  
            r'\d+\.\d+\.\w+',              
            r'\d+\.\w+',                   
            r'v?\d{1,3}(?!\d)'             
        ]

#    def extract_versions_with_context(self, text, context_length=30):
#        """
#        Находит версии в тексте и извлекает окружающий их контекст.
#        
#        Args:
#            text (str): Текст для анализа
#            context_length (int): Количество символов контекста до и после версии
#        
#        Returns:
#            list: Список найденных версий с контекстом
#        """
#        # Шаблон для поиска версий (поддерживает форматы вида 1.2.3, v1.2.3, версия 1.2 и т.д.)
#        version_pattern = r'(?:v|версия|version)?\s*\d+(?:\.\d+)+(?:-\w+)?'
#        
#        results = []
#        
#        # Поиск всех соответствий шаблону в тексте
#        for match in re.finditer(version_pattern, text, re.IGNORECASE):
#            version = match.group(0)
#            start_pos = match.start()
#            end_pos = match.end()
#            
#            # Вычисление границ контекста
#            context_start = max(0, start_pos - context_length)
#            context_end = min(len(text), end_pos + context_length)
#            
#            # Извлечение контекста
#            context = text[context_start:context_end]
#            
#            # Добавление информации о найденной версии
#            results.append({
#                'version': version,
#                'context': context,
#                'position': (start_pos, end_pos)
#            })
#        
#        return results

    def _extract_possible(self, data: str):
        info("Extracting possible versions")

        software_pattern = r'[A-Za-z][\w\.\+\-\#]+ [A-Za-z][\w\.\+\-\#]+'
        
        version_keywords = [
            r'latest', r'version', r'release', r'stable', r'updated', r'current',
            r'lts', r'beta', r'alpha', r'rc\d*', r'build', r'update'
        ]
        
        version_pattern = '|'.join(self.version_patterns)
        keyword_pattern = '|'.join(version_keywords)
        
        context_words = r'(?:версии|version|ver\.|v\.|release|rel\.|for|of|на|with)'
        
        patterns = [
            rf'(?<!\w)({software_pattern})\s+(?:{keyword_pattern}\s+)?(?:{context_words}\s+)?({version_pattern})(?!\w)',
            rf'(?<!\w)({version_pattern})\s+(?:{keyword_pattern}\s+)?(?:{context_words}\s+)?({software_pattern})(?!\w)',
            rf'(?<!\w)({software_pattern})\s+{context_words}\s+({version_pattern})(?!\w)',
            rf'(?<!\w)({version_pattern})\s+{context_words}\s+({software_pattern})(?!\w)',
            rf'(?<!\w)({software_pattern})\s+({keyword_pattern})\s+({version_pattern})(?!\w)',
            rf'(?<!\w)({software_pattern})\s+({keyword_pattern})\s+({version_pattern})(?!\w)',
            rf'(?<!\w)({software_pattern})\s+({version_pattern})(?!\w)',
        ]
        
        all_matches = []
        for pattern in patterns:
            matches = re.finditer(pattern, data, re.IGNORECASE)
            for match in matches:
                full_match = match.group(0).strip()
                
                has_version = any(re.search(vp, full_match, re.IGNORECASE) for vp in self.version_patterns)
                potential_software = re.search(r'\b[A-Za-z]\w+\b', full_match, re.IGNORECASE)
                
                if has_version and potential_software:
                    normalized_match = re.sub(r'\s+', ' ', full_match)
                    all_matches.append(normalized_match)
        
        unique_matches = []
        for match in all_matches:
            is_substring = False
            for other in all_matches:
                if match != other and match in other:
                    match_words = set(re.findall(r'\b\w+\b', match))
                    other_words = set(re.findall(r'\b\w+\b', other))
                    if match_words.issubset(other_words) and len(match) < len(other):
                        is_substring = True
                        break
            
            if not is_substring and match not in unique_matches:
                unique_matches.append(match)

        info("Extracted: %s", str(unique_matches))
        
        return unique_matches

    def _select_by_gpt(self, name: str, extracted: str):
        info("Extracting version using GPT")
        try:
            prompt = {
                "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
                "completionOptions": {
                    "temperature": 0,
                    "maxTokens": 300
                },
                "messages": [
                    {
                        "role": "system",
                        "text": (
                            f"Определи последнюю версию {name}.\n"
                            "Правила:\n1. Только числовые версии\n"
                            "2. Формат: X.Y.Z"
                        )
                    },
                    {
                        "role": "user",
                        "text": extracted
                    }
                ]
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=prompt,
                timeout=15
            )
            response.raise_for_status()
            
            result = response.json()
            gpt_response = result['result']['alternatives'][0]['message']['text']
            info("GPT Raw Response: %s", gpt_response)

            # Enhanced post-GPT validation with multiple patterns
            best_match = None
            for pattern in self.version_patterns:
                match = re.search(pattern, gpt_response, re.IGNORECASE)
                if match:
                    best_match = match.group(0).lstrip('v').strip()
                    info("Pattern %s matched: %s", pattern, best_match)
                    break

            if best_match:
                # Clean up version format
                clean_version = re.sub(r'\s+', '', best_match)  # Remove any whitespace
                info("Validated version after GPT: %s", clean_version)
                return clean_version

            warning("No valid version found in GPT response")
            return None

        except Exception as e:
            warning("GPT analysis failed: %s", str(e))
            return None


    def analyze(self, name: str, contents: List[str]):
        extracted_data = []
        for data in contents:
            extracted_data += self._extract_possible(data)

        if not extracted_data:
            info("No version candidates found in input")
            return None

        # Prioritize matches with more components
        unique_matches = sorted(
            list(set(extracted_data)),
            key=lambda x: (-len(x.split()), len(x)),
            reverse=True
        )[:20]  # Take top 15 most specific candidates
        
        extracted_str = "\n".join(unique_matches)
        info("Sending to GPT: %s", extracted_str)

        return self._select_by_gpt(name, extracted_str)
