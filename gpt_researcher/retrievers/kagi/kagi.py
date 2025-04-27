# Kagi Search Retriever

# libraries
import os
import requests
import json
import logging


class KagiSearch():
    """
    Kagi Search Retriever
    """

    def __init__(self, query, query_domains=None):
        """
        Initializes the KagiSearch object
        Args:
            query: Search query
            query_domains: Optional list of domains to filter the search results
        """
        self.query = query
        self.query_domains = query_domains or None
        self.api_key = self.get_api_key()
        self.logger = logging.getLogger(__name__)

    def get_api_key(self):
        """
        Gets the Kagi API key from environment variables
        Returns:
            API key string
        """
        try:
            api_key = os.environ["KAGI_API_KEY"]
        except:
            raise Exception(
                "Kagi API key not found. Please set the KAGI_API_KEY environment variable.")
        return api_key

    def search(self, max_results=10) -> list[dict[str]]:
        """
        Searches the query using Kagi Search API
        Args:
            max_results: Maximum number of results to return
        Returns:
            List of search results in normalized format
        """
        print("Searching with query {0}...".format(self.query))
        """Useful for general internet search queries using the Kagi API."""

        # Search the query
        url = "https://kagi.com/api/v0/search"

        headers = {
            "Authorization": f"Bot {self.api_key}",
            "Content-Type": "application/json"
        }
        
        params = {
            "q": self.query,
            "limit": max_results
        }
        
        # Add domain filter if specified
        if self.query_domains:
            domain_filter = " ".join([f"site:{domain}" for domain in self.query_domains])
            params["q"] = f"{params['q']} {domain_filter}"

        try:
            resp = requests.get(url, headers=headers, params=params)
            resp.raise_for_status()  # Raise an exception for HTTP errors
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error making request to Kagi API: {e}")
            return []

        # Preprocess the results
        search_results = []
        
        try:
            result_data = json.loads(resp.text)
            
            if "data" not in result_data:
                self.logger.warning(f"No search results found for query: {self.query}")
                return []
            
            # Process web search results (t=0 indicates web results in Kagi API)
            for item in result_data["data"]:
                if item.get("t") == 0:  # Web results have type 0
                    search_result = {
                        "title": item.get("title", ""),
                        "href": item.get("url", ""),
                        "body": item.get("snippet", ""),
                    }
                    
                        
                    search_results.append(search_result)
                    
                    # Break if we have reached max_results
                    if len(search_results) >= max_results:
                        break
                        
        except Exception as e:
            self.logger.error(
                f"Error parsing Kagi search results: {e}. Resulting in empty response.")
            return []
            
        return search_results
