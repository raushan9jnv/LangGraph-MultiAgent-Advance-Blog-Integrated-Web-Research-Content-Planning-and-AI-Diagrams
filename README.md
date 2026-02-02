
# LangGraph-MultiAgent-Advance-Blog-Integrated-Web-Research-Content-Planning-and-AI-Diagrams" 
# Details

# Multimodal Blog Writer using LangGraph + Gemini

A production-style, agentic blog generation system built with LangGraph and Google Gemini.
The system can optionally perform web research, generate structured technical blogs,
and automatically create and embed diagrams using Gemini Image models.

--------------------------------------------------
KEY FEATURES
--------------------------------------------------
- Intelligent routing (closed_book / hybrid / open_book)
- Optional web research with recency filtering
- Structured planning via an orchestrator agent
- Parallel section generation using fanout
- Reducer subgraph for merging and image insertion
- Multimodal output (text + images)
- Markdown-ready blog output

--------------------------------------------------
HIGH-LEVEL ARCHITECTURE
--------------------------------------------------

<img width="1008" height="853" alt="image" src="https://github.com/user-attachments/assets/bae41043-6417-484f-9577-48de750f1243" />

<img width="906" height="906" alt="image" src="https://github.com/user-attachments/assets/c2de5819-626b-4f92-b717-40e08f75ac3e" />

<img width="160" height="630" alt="image" src="https://github.com/user-attachments/assets/616c4a2c-9861-41fc-91cb-354c70baa009" />

--------------------------------------------------
AGENT OVERVIEW
--------------------------------------------------

1. Router Node
- Decides whether web research is required
- Determines execution mode:
  - closed_book
  - hybrid
  - open_book
- Outputs queries and recency window

Gemini model used:
- gemini-2.5-flash

--------------------------------------------------

2. Research Node (Optional)
- Uses Tavily Search API
- Collects URLs, snippets, publication dates
- Filters evidence based on recency
- Produces structured EvidenceItem objects

Gemini model used:
- gemini-2.5-flash (for synthesis and normalization)

--------------------------------------------------

3. Orchestrator (Planner Agent)
- Converts topic into a structured blog plan
- Defines:
  - Blog title
  - Audience
  - Tone
  - 5–9 tasks
  - Word limits
  - Citation and code requirements

Acts as the single source of truth for the pipeline.

Gemini model used:
- gemini-2.5-flash

--------------------------------------------------
FANOUT (PARALLEL EXECUTION)
--------------------------------------------------

Fanout means:
- One planning decision
- Multiple worker agents running in parallel

Each task is sent using LangGraph's Send() API.
This follows a Map–Reduce pattern:
- Map phase: Workers
- Reduce phase: ReducerWithImages

Benefits:
- Parallelism
- Isolation per section
- Better quality control
- Easy scalability

--------------------------------------------------
WORKER NODES
--------------------------------------------------

Each worker:
- Writes exactly one blog section
- Covers all assigned bullets
- Respects word limits
- Enforces citation rules
- Outputs markdown starting with:
  "## Section Title"

Gemini model used:
- gemini-2.5-flash

--------------------------------------------------
REDUCER WITH IMAGES (SUBGRAPH)
--------------------------------------------------

The reducer is implemented as a LangGraph subgraph.

Reducer flow:
- merge_content
- decide_images
- generate_and_place_images

--------------------------------------------------

merge_content
- Orders sections by task ID
- Merges all sections into one markdown body

--------------------------------------------------

decide_images
- Decides if diagrams are needed
- Inserts placeholders:
  [[IMAGE_1]], [[IMAGE_2]], [[IMAGE_3]]
- Generates structured image prompts

Gemini model used:
- gemini-2.5-flash

--------------------------------------------------

generate_and_place_images
- Calls Gemini Image API
- Generates diagrams
- Saves images under /images
- Replaces placeholders with markdown image tags
- Falls back gracefully if image generation fails

Gemini model used:
- gemini-2.5-flash-image

--------------------------------------------------
GEMINI MODEL USAGE SUMMARY
--------------------------------------------------

gemini-2.5-flash
- Router (decision making)
- Research synthesis
- Orchestrator planning
- Worker section writing
- Image planning (decide_images)

gemini-2.5-flash-image
- Diagram and image generation

--------------------------------------------------
PROJECT STRUCTURE
--------------------------------------------------

.
├── images/                 # Generated images
├── blog_title_slug.md      # Final markdown output
├── app.py                  # LangGraph pipeline
├── .env                    # API keys
└── README.md

--------------------------------------------------
ENVIRONMENT VARIABLES
--------------------------------------------------

GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key   (optional)

--------------------------------------------------
HOW TO RUN
--------------------------------------------------

app.invoke({
    "topic": "Latest trends in Agentic AI",
    "as_of": "2026-02-02"
})

Output:
- Final markdown blog
- Images auto-generated if required
- Files saved locally

--------------------------------------------------
WHY THIS DESIGN
--------------------------------------------------
- Cost-efficient (Flash model everywhere)
- Parallel and scalable
- Evidence-grounded
- Multimodal output
- Production-grade LangGraph usage

 # Result after Running

## Plan
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/1b9799af-cb65-4cd1-a235-f5111e947d96" />

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/c9c2b2a9-3bf4-43c2-9696-3e9c663db892" />


## Evidence
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/a21b27f3-b983-4769-8547-93b44dbab75d" />

## Markdown preview
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/6e05d775-b914-41bc-bced-5d465a973e92" />


## Images
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/f0956678-fa56-41bf-a5d6-2bb73ea855e6" />

## logs
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/6cf8a9fb-6666-467e-ba08-96ba91e29d2b" />


--------------------------------------------------
FUTURE ENHANCEMENTS
--------------------------------------------------
- SEO optimization agent
- Factual consistency checker
- CMS publishing (WordPress, Notion)
- Human-in-the-loop review
- Streaming output
