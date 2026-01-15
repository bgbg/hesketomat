"""API endpoints for Search functionality."""
import logging
from fastapi import APIRouter, HTTPException
from backend.models.interview_schemas import (
    SearchRequest,
    SearchResponse,
    WebSearchResult,
    ImageSearchResult,
    SearchCitation,
)
from backend.services.search_service import search_service
from backend.services.llm_service import llm_service
from backend.services.image_service import image_service
from backend.services.prompt_loader import prompt_loader

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    """
    Perform web search with AI-generated summary.

    Steps:
    1. Search using Tavily API
    2. Generate AI summary with citations using selected LLM provider
    3. Extract images from search results
    4. Return unified response
    """
    logger.info(f"Search request: query='{request.query}', provider={request.llm_provider}")

    try:
        # Step 1: Perform web search
        search_results = search_service.search(
            query=request.query,
            max_results=10,
            include_images=True,
        )

        # Step 2: Format search results for LLM
        formatted_results = []
        citations_map = {}  # URL to citation number mapping

        for idx, result in enumerate(search_results["results"], 1):
            citations_map[result["url"]] = idx
            formatted_results.append(
                f"[{idx}] {result['title']}\n"
                f"Source: {result['domain']}\n"
                f"Content: {result['snippet']}\n"
            )

        search_results_text = "\n".join(formatted_results)

        # Step 3: Generate AI summary using LLM
        system_prompt, user_prompt = prompt_loader.get_search_summary_prompts(
            query=request.query,
            search_results=search_results_text,
            background_context=request.background_context,
        )

        summary_text = llm_service.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            provider=request.llm_provider.value,
            max_tokens=300,
            temperature=0.7,
        )

        # Step 4: Extract citations from summary
        citations = []
        for url, citation_num in sorted(citations_map.items(), key=lambda x: x[1]):
            # Find the corresponding result
            result = next(
                (r for r in search_results["results"] if r["url"] == url),
                None
            )
            if result and f"[{citation_num}]" in summary_text:
                citations.append(
                    SearchCitation(
                        number=citation_num,
                        title=result["title"],
                        url=result["url"],
                    )
                )

        # Step 5: Format web results
        web_results = [
            WebSearchResult(
                title=r["title"],
                url=r["url"],
                snippet=r["snippet"],
                domain=r["domain"],
            )
            for r in search_results["results"]
        ]

        # Step 6: Format image results
        image_results = [
            ImageSearchResult(
                url=img["url"],
                thumbnail_url=img["thumbnail_url"],
                title=img.get("title"),
                source_url=img.get("source_url"),
            )
            for img in image_service.filter_images(search_results["images"], max_count=10)
        ]

        logger.info(
            f"Search completed: {len(web_results)} results, "
            f"{len(image_results)} images, {len(citations)} citations"
        )

        return SearchResponse(
            summary=summary_text,
            citations=citations,
            web_results=web_results,
            image_results=image_results,
        )

    except ValueError as e:
        # Configuration errors (missing API keys, etc.)
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Search error for query '{request.query}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed. Please try again.")
