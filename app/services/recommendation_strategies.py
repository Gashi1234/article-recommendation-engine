from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from app.models.article import Article

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from dataclasses import dataclass
from typing import List



class RecommendationStrategy(Protocol):
    def recommend(self, article_id: int, limit: int = 5) -> List[Article]:
        ...


@dataclass
class PopularityStrategy:
    article_service: any
    event_service: any

    def recommend(self, article_id: int, limit: int = 5) -> List[Article]:
        all_articles = self.article_service.list_articles()

        scored = []
        for a in all_articles:
            if a.id == article_id:
                continue

            views = self.event_service.count_for_article(a.id, "view")
            likes = self.event_service.count_for_article(a.id, "like")
            total_ms = self.event_service.total_duration_ms_for_article(a.id, "time_spent")

            time_minutes = total_ms / 60000.0
            if time_minutes > 10:
                time_minutes = 10

            score = (views * 1) + (likes * 3) + (time_minutes * 2)
            
            scored.append((score, a))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [a for score, a in scored[:limit]]


@dataclass
class ContentBasedStrategy:
    article_service: any

    def recommend(self, article_id: int, limit: int = 5) -> List[Article]:
        current = self.article_service.get_article(article_id)
        if not current:
            return []

        all_articles = self.article_service.list_articles()
        if not all_articles:
            return []

        # text = title + content + category_name
        def build_text(a: Article) -> str:
            title = (a.title or "").strip()
            content = (a.content or "").strip()
            category = (a.category_name or "").strip()
            return f"{title} {content} {category}".strip()

        texts = [build_text(a) for a in all_articles]

        idx = None
        for i, a in enumerate(all_articles):
            if a.id == article_id:
                idx = i
                break
        if idx is None:
            return []

        vectorizer = TfidfVectorizer(
            lowercase=True,
            max_features=5000,
            stop_words="english"
        )
        tfidf_matrix = vectorizer.fit_transform(texts)

        sims = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()

        current_category_id = getattr(current, "category_id", None)

        same_category_scored = []
        other_scored = []

        for i, sim in enumerate(sims):
            a = all_articles[i]
            if a.id == article_id:
                continue

            item = (float(sim), a)

            if current_category_id is not None and getattr(a, "category_id", None) == current_category_id:
                same_category_scored.append(item)
            else:
                other_scored.append(item)

        same_category_scored.sort(key=lambda x: x[0], reverse=True)
        other_scored.sort(key=lambda x: x[0], reverse=True)

        ranked = same_category_scored + other_scored
        return [a for score, a in ranked[:limit]]
    
@dataclass
class HybridStrategy:
        content_strategy: any
        popularity_strategy: any

        def recommend(self, article_id: int, limit: int = 5) -> List[Article]:
            content_recs = self.content_strategy.recommend(article_id=article_id, limit=limit)
            pop_recs = self.popularity_strategy.recommend(article_id=article_id, limit=limit)

            merged = []
            seen = set()

            i = 0
            while len(merged) < limit and (i < len(content_recs) or i < len(pop_recs)):
                if i < len(content_recs):
                    a = content_recs[i]
                    if a.id != article_id and a.id not in seen:
                        seen.add(a.id)
                        merged.append(a)
                        if len(merged) >= limit:
                            break

                if i < len(pop_recs):
                    a = pop_recs[i]
                    if a.id != article_id and a.id not in seen:
                        seen.add(a.id)
                        merged.append(a)
                        if len(merged) >= limit:
                            break

                i += 1

            return merged


