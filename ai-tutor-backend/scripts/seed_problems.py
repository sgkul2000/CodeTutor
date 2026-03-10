"""
Seed script: populates MongoDB with 10 canonical DSA problems.
Run from ai-tutor-backend/ directory:
    python -m scripts.seed_problems
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.config import settings
from app.models.problem import Problem, Example, TestCase, StarterCode, HintsMetadata

PROBLEMS = [
    {
        "title": "Two Sum",
        "slug": "two-sum",
        "difficulty": "easy",
        "category": ["array", "hash-map"],
        "description": (
            "Given an array of integers `nums` and an integer `target`, "
            "return **indices** of the two numbers such that they add up to `target`.\n\n"
            "You may assume that each input would have **exactly one solution**, "
            "and you may not use the same element twice.\n\n"
            "You can return the answer in any order."
        ),
        "constraints": "2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9\n-10^9 <= target <= 10^9\nOnly one valid answer exists.",
        "examples": [
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "explanation": "nums[0] + nums[1] = 9"},
            {"input": "nums = [3,2,4], target = 6", "output": "[1,2]"},
        ],
        "test_cases": [
            {"input": "[2,7,11,15]\n9", "expected_output": "[0,1]"},
            {"input": "[3,2,4]\n6", "expected_output": "[1,2]"},
            {"input": "[3,3]\n6", "expected_output": "[0,1]"},
            {"input": "[1,2,3,4,5]\n9", "expected_output": "[3,4]"},
            {"input": "[-1,-2,-3,-4,-5]\n-8", "expected_output": "[2,4]"},
        ],
        "starter_code": {
            "python": "class Solution:\n    def twoSum(self, nums: list[int], target: int) -> list[int]:\n        pass",
            "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        \n    }\n}",
            "javascript": "/**\n * @param {number[]} nums\n * @param {number} target\n * @return {number[]}\n */\nvar twoSum = function(nums, target) {\n    \n};",
        },
        "hints_metadata": {
            "common_mistakes": ["Nested loop O(n²) approach", "Not handling duplicate values"],
            "key_insight": "Use a hash map to look up the complement in O(1)",
            "related_problems": ["three-sum", "two-sum-ii"],
        },
    },
    {
        "title": "Valid Parentheses",
        "slug": "valid-parentheses",
        "difficulty": "easy",
        "category": ["stack-queue", "string"],
        "description": (
            "Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, "
            "determine if the input string is valid.\n\n"
            "An input string is valid if:\n"
            "1. Open brackets must be closed by the same type of brackets.\n"
            "2. Open brackets must be closed in the correct order.\n"
            "3. Every close bracket has a corresponding open bracket of the same type."
        ),
        "constraints": "1 <= s.length <= 10^4\ns consists of parentheses only '()[]{}'.",
        "examples": [
            {"input": 's = "()"', "output": "true"},
            {"input": 's = "()[]{}"', "output": "true"},
            {"input": 's = "(]"', "output": "false"},
        ],
        "test_cases": [
            {"input": "()", "expected_output": "true"},
            {"input": "()[]{}", "expected_output": "true"},
            {"input": "(]", "expected_output": "false"},
            {"input": "([)]", "expected_output": "false"},
            {"input": "{[]}", "expected_output": "true"},
            {"input": "", "expected_output": "true"},
        ],
        "starter_code": {
            "python": "class Solution:\n    def isValid(self, s: str) -> bool:\n        pass",
            "java": "class Solution {\n    public boolean isValid(String s) {\n        \n    }\n}",
            "javascript": "var isValid = function(s) {\n    \n};",
        },
        "hints_metadata": {
            "common_mistakes": ["Not handling empty string", "Using a queue instead of a stack"],
            "key_insight": "Use a stack — push open brackets, pop and match on close brackets",
            "related_problems": ["longest-valid-parentheses", "generate-parentheses"],
        },
    },
    {
        "title": "Reverse Linked List",
        "slug": "reverse-linked-list",
        "difficulty": "easy",
        "category": ["linked-list"],
        "description": (
            "Given the `head` of a singly linked list, reverse the list, and return the reversed list.\n\n"
            "**Example:**\n```\nInput:  1 -> 2 -> 3 -> 4 -> 5\nOutput: 5 -> 4 -> 3 -> 2 -> 1\n```"
        ),
        "constraints": "The number of nodes in the list is in the range [0, 5000].\n-5000 <= Node.val <= 5000.",
        "examples": [
            {"input": "head = [1,2,3,4,5]", "output": "[5,4,3,2,1]"},
            {"input": "head = [1,2]", "output": "[2,1]"},
            {"input": "head = []", "output": "[]"},
        ],
        "test_cases": [
            {"input": "[1,2,3,4,5]", "expected_output": "[5,4,3,2,1]"},
            {"input": "[1,2]", "expected_output": "[2,1]"},
            {"input": "[]", "expected_output": "[]"},
            {"input": "[1]", "expected_output": "[1]"},
        ],
        "starter_code": {
            "python": "# Definition for singly-linked list.\n# class ListNode:\n#     def __init__(self, val=0, next=None):\n#         self.val = val\n#         self.next = next\nclass Solution:\n    def reverseList(self, head):\n        pass",
            "java": "class Solution {\n    public ListNode reverseList(ListNode head) {\n        \n    }\n}",
            "javascript": "var reverseList = function(head) {\n    \n};",
        },
        "hints_metadata": {
            "common_mistakes": ["Losing reference to next node before updating pointer", "Forgetting the iterative vs recursive distinction"],
            "key_insight": "Use three pointers: prev, curr, next to reverse links in-place",
            "related_problems": ["reverse-linked-list-ii", "palindrome-linked-list"],
        },
    },
    {
        "title": "Maximum Subarray",
        "slug": "maximum-subarray",
        "difficulty": "medium",
        "category": ["array", "dynamic-programming"],
        "description": (
            "Given an integer array `nums`, find the **subarray** with the largest sum, and return its sum.\n\n"
            "A **subarray** is a contiguous non-empty sequence of elements within an array."
        ),
        "constraints": "1 <= nums.length <= 10^5\n-10^4 <= nums[i] <= 10^4",
        "examples": [
            {"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6", "explanation": "Subarray [4,-1,2,1] has the largest sum 6"},
            {"input": "nums = [1]", "output": "1"},
            {"input": "nums = [5,4,-1,7,8]", "output": "23"},
        ],
        "test_cases": [
            {"input": "[-2,1,-3,4,-1,2,1,-5,4]", "expected_output": "6"},
            {"input": "[1]", "expected_output": "1"},
            {"input": "[5,4,-1,7,8]", "expected_output": "23"},
            {"input": "[-1,-2,-3,-4]", "expected_output": "-1"},
            {"input": "[0,0,0]", "expected_output": "0"},
        ],
        "starter_code": {
            "python": "class Solution:\n    def maxSubArray(self, nums: list[int]) -> int:\n        pass",
            "java": "class Solution {\n    public int maxSubArray(int[] nums) {\n        \n    }\n}",
            "javascript": "var maxSubArray = function(nums) {\n    \n};",
        },
        "hints_metadata": {
            "common_mistakes": ["Using brute force O(n²)", "Resetting current sum to 0 instead of the current element when negative"],
            "key_insight": "Kadane's algorithm: track current sum, reset to current element when current sum goes negative",
            "related_problems": ["maximum-product-subarray", "best-time-to-buy-and-sell-stock"],
        },
    },
    {
        "title": "Binary Search",
        "slug": "binary-search",
        "difficulty": "easy",
        "category": ["binary-search", "array"],
        "description": (
            "Given an array of integers `nums` which is sorted in ascending order, "
            "and an integer `target`, write a function to search `target` in `nums`. "
            "If `target` exists, then return its index. Otherwise, return `-1`.\n\n"
            "You must write an algorithm with `O(log n)` runtime complexity."
        ),
        "constraints": "1 <= nums.length <= 10^4\n-10^4 < nums[i], target < 10^4\nAll the integers in nums are unique.\nnums is sorted in ascending order.",
        "examples": [
            {"input": "nums = [-1,0,3,5,9,12], target = 9", "output": "4"},
            {"input": "nums = [-1,0,3,5,9,12], target = 2", "output": "-1"},
        ],
        "test_cases": [
            {"input": "[-1,0,3,5,9,12]\n9", "expected_output": "4"},
            {"input": "[-1,0,3,5,9,12]\n2", "expected_output": "-1"},
            {"input": "[5]\n5", "expected_output": "0"},
            {"input": "[5]\n3", "expected_output": "-1"},
            {"input": "[1,2,3,4,5,6,7,8,9,10]\n1", "expected_output": "0"},
        ],
        "starter_code": {
            "python": "class Solution:\n    def search(self, nums: list[int], target: int) -> int:\n        pass",
            "java": "class Solution {\n    public int search(int[] nums, int target) {\n        \n    }\n}",
            "javascript": "var search = function(nums, target) {\n    \n};",
        },
        "hints_metadata": {
            "common_mistakes": ["Off-by-one errors on boundary conditions", "Infinite loop when mid calculation doesn't converge", "Not handling single-element arrays"],
            "key_insight": "Use left + (right - left) // 2 to avoid integer overflow; narrow the search space by half each iteration",
            "related_problems": ["search-in-rotated-sorted-array", "find-minimum-in-rotated-sorted-array"],
        },
    },
    {
        "title": "Number of Islands",
        "slug": "number-of-islands",
        "difficulty": "medium",
        "category": ["graph", "array"],
        "description": (
            "Given an `m x n` 2D binary grid `grid` which represents a map of `'1'`s (land) "
            "and `'0'`s (water), return the number of islands.\n\n"
            "An **island** is surrounded by water and is formed by connecting adjacent lands "
            "horizontally or vertically. You may assume all four edges of the grid are all surrounded by water."
        ),
        "constraints": "m == grid.length\nn == grid[i].length\n1 <= m, n <= 300\ngrid[i][j] is '0' or '1'.",
        "examples": [
            {"input": 'grid = [["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]', "output": "1"},
            {"input": 'grid = [["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]', "output": "3"},
        ],
        "test_cases": [
            {"input": '["1","1","1","1","0"]\n["1","1","0","1","0"]\n["1","1","0","0","0"]\n["0","0","0","0","0"]', "expected_output": "1"},
            {"input": '["1","1","0","0","0"]\n["1","1","0","0","0"]\n["0","0","1","0","0"]\n["0","0","0","1","1"]', "expected_output": "3"},
            {"input": '["1"]', "expected_output": "1"},
            {"input": '["0"]', "expected_output": "0"},
        ],
        "starter_code": {
            "python": "class Solution:\n    def numIslands(self, grid: list[list[str]]) -> int:\n        pass",
            "java": "class Solution {\n    public int numIslands(char[][] grid) {\n        \n    }\n}",
            "javascript": "var numIslands = function(grid) {\n    \n};",
        },
        "hints_metadata": {
            "common_mistakes": ["Visiting the same cell multiple times", "Not marking visited cells", "Forgetting boundary checks"],
            "key_insight": "BFS or DFS from each unvisited land cell, marking visited cells to avoid revisiting",
            "related_problems": ["max-area-of-island", "surrounded-regions"],
        },
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "slug": "longest-substring-without-repeating-characters",
        "difficulty": "medium",
        "category": ["sliding-window", "hash-map", "string"],
        "description": (
            "Given a string `s`, find the length of the **longest substring** without repeating characters."
        ),
        "constraints": "0 <= s.length <= 5 * 10^4\ns consists of English letters, digits, symbols and spaces.",
        "examples": [
            {"input": 's = "abcabcbb"', "output": "3", "explanation": "The answer is 'abc', with length 3."},
            {"input": 's = "bbbbb"', "output": "1", "explanation": "The answer is 'b', with length 1."},
            {"input": 's = "pwwkew"', "output": "3", "explanation": "The answer is 'wke', with length 3."},
        ],
        "test_cases": [
            {"input": "abcabcbb", "expected_output": "3"},
            {"input": "bbbbb", "expected_output": "1"},
            {"input": "pwwkew", "expected_output": "3"},
            {"input": "", "expected_output": "0"},
            {"input": "au", "expected_output": "2"},
        ],
        "starter_code": {
            "python": "class Solution:\n    def lengthOfLongestSubstring(self, s: str) -> int:\n        pass",
            "java": "class Solution {\n    public int lengthOfLongestSubstring(String s) {\n        \n    }\n}",
            "javascript": "var lengthOfLongestSubstring = function(s) {\n    \n};",
        },
        "hints_metadata": {
            "common_mistakes": ["Using nested loops O(n²)", "Not updating the left pointer correctly when a duplicate is found"],
            "key_insight": "Sliding window with a hash map tracking each character's last seen index; jump left pointer past the duplicate",
            "related_problems": ["longest-substring-with-at-most-two-distinct-characters", "minimum-window-substring"],
        },
    },
    {
        "title": "Merge Intervals",
        "slug": "merge-intervals",
        "difficulty": "medium",
        "category": ["array", "sorting"],
        "description": (
            "Given an array of `intervals` where `intervals[i] = [starti, endi]`, "
            "merge all overlapping intervals, and return an array of the non-overlapping intervals "
            "that cover all the intervals in the input."
        ),
        "constraints": "1 <= intervals.length <= 10^4\nintervals[i].length == 2\n0 <= starti <= endi <= 10^4",
        "examples": [
            {"input": "intervals = [[1,3],[2,6],[8,10],[15,18]]", "output": "[[1,6],[8,10],[15,18]]", "explanation": "Intervals [1,3] and [2,6] overlap, merged to [1,6]."},
            {"input": "intervals = [[1,4],[4,5]]", "output": "[[1,5]]"},
        ],
        "test_cases": [
            {"input": "[[1,3],[2,6],[8,10],[15,18]]", "expected_output": "[[1,6],[8,10],[15,18]]"},
            {"input": "[[1,4],[4,5]]", "expected_output": "[[1,5]]"},
            {"input": "[[1,4],[2,3]]", "expected_output": "[[1,4]]"},
            {"input": "[[1,4]]", "expected_output": "[[1,4]]"},
            {"input": "[[1,4],[0,4]]", "expected_output": "[[0,4]]"},
        ],
        "starter_code": {
            "python": "class Solution:\n    def merge(self, intervals: list[list[int]]) -> list[list[int]]:\n        pass",
            "java": "class Solution {\n    public int[][] merge(int[][] intervals) {\n        \n    }\n}",
            "javascript": "var merge = function(intervals) {\n    \n};",
        },
        "hints_metadata": {
            "common_mistakes": ["Forgetting to sort first", "Off-by-one when checking overlap (start <= end vs start < end)"],
            "key_insight": "Sort by start time, then greedily merge: if current start <= last merged end, extend the end",
            "related_problems": ["insert-interval", "non-overlapping-intervals"],
        },
    },
    {
        "title": "Climbing Stairs",
        "slug": "climbing-stairs",
        "difficulty": "easy",
        "category": ["dynamic-programming"],
        "description": (
            "You are climbing a staircase. It takes `n` steps to reach the top.\n\n"
            "Each time you can either climb `1` or `2` steps. "
            "In how many distinct ways can you climb to the top?"
        ),
        "constraints": "1 <= n <= 45",
        "examples": [
            {"input": "n = 2", "output": "2", "explanation": "1+1, 2"},
            {"input": "n = 3", "output": "3", "explanation": "1+1+1, 1+2, 2+1"},
        ],
        "test_cases": [
            {"input": "2", "expected_output": "2"},
            {"input": "3", "expected_output": "3"},
            {"input": "1", "expected_output": "1"},
            {"input": "10", "expected_output": "89"},
            {"input": "45", "expected_output": "1836311903"},
        ],
        "starter_code": {
            "python": "class Solution:\n    def climbStairs(self, n: int) -> int:\n        pass",
            "java": "class Solution {\n    public int climbStairs(int n) {\n        \n    }\n}",
            "javascript": "var climbStairs = function(n) {\n    \n};",
        },
        "hints_metadata": {
            "common_mistakes": ["Using naive recursion (exponential time)", "Not recognizing the Fibonacci pattern"],
            "key_insight": "dp[n] = dp[n-1] + dp[n-2]; the answer at step n depends only on the last two steps",
            "related_problems": ["min-cost-climbing-stairs", "fibonacci-number"],
        },
    },
    {
        "title": "Word Ladder",
        "slug": "word-ladder",
        "difficulty": "hard",
        "category": ["graph", "string"],
        "description": (
            "A **transformation sequence** from word `beginWord` to word `endWord` using a dictionary `wordList` "
            "is a sequence of words `beginWord -> s1 -> s2 -> ... -> sk` such that:\n"
            "- Every adjacent pair of words differs by a single letter.\n"
            "- Every `si` for `1 <= i <= k` is in `wordList`. Note that `beginWord` does not need to be in `wordList`.\n"
            "- `sk == endWord`\n\n"
            "Given two words, `beginWord` and `endWord`, and a dictionary `wordList`, "
            "return the **number of words** in the shortest transformation sequence from `beginWord` to `endWord`, "
            "or `0` if no such sequence exists."
        ),
        "constraints": "1 <= beginWord.length <= 10\nendWord.length == beginWord.length\n1 <= wordList.length <= 5000\nwordList[i].length == beginWord.length\nbeginWord, endWord, and wordList[i] consist of lowercase English letters.\nbeginWord != endWord\nAll the words in wordList are unique.",
        "examples": [
            {"input": 'beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]', "output": "5", "explanation": "hit -> hot -> dot -> dog -> cog"},
            {"input": 'beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log"]', "output": "0", "explanation": "endWord not in wordList"},
        ],
        "test_cases": [
            {"input": "hit\ncog\nhot dot dog lot log cog", "expected_output": "5"},
            {"input": "hit\ncog\nhot dot dog lot log", "expected_output": "0"},
            {"input": "a\nc\na b c", "expected_output": "2"},
        ],
        "starter_code": {
            "python": "class Solution:\n    def ladderLength(self, beginWord: str, endWord: str, wordList: list[str]) -> int:\n        pass",
            "java": "class Solution {\n    public int ladderLength(String beginWord, String endWord, List<String> wordList) {\n        \n    }\n}",
            "javascript": "var ladderLength = function(beginWord, endWord, wordList) {\n    \n};",
        },
        "hints_metadata": {
            "common_mistakes": ["Using DFS instead of BFS (BFS guarantees shortest path)", "Not building the word graph efficiently"],
            "key_insight": "BFS from beginWord; for each word generate all one-letter mutations and check if they're in the word set",
            "related_problems": ["word-ladder-ii", "minimum-genetic-mutation"],
        },
    },
]


async def seed():
    client = AsyncIOMotorClient(settings.mongodb_uri)
    await init_beanie(
        database=client[settings.mongodb_database],
        document_models=[Problem],
    )

    inserted = 0
    skipped = 0
    for data in PROBLEMS:
        existing = await Problem.find_one(Problem.slug == data["slug"])
        if existing:
            print(f"  SKIP  {data['slug']} (already exists)")
            skipped += 1
            continue

        problem = Problem(
            title=data["title"],
            slug=data["slug"],
            difficulty=data["difficulty"],
            category=data["category"],
            description=data["description"],
            constraints=data["constraints"],
            examples=[Example(**e) for e in data["examples"]],
            test_cases=[TestCase(**tc) for tc in data["test_cases"]],
            starter_code=StarterCode(**data["starter_code"]),
            hints_metadata=HintsMetadata(**data["hints_metadata"]),
        )
        await problem.insert()
        print(f"  OK    {data['slug']}")
        inserted += 1

    print(f"\nDone: {inserted} inserted, {skipped} skipped.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
