"""
EcoWatcher — Multi-Agent ADK Rendering Engine
===============================================
# Day 3 Concept: ADK Multi-Agent Handoff Loop
# Day 2 Concept: MCP Local Tool Binding
# Day 1 Concept: Foundational GenAI API Integration

This module architects a 3-agent pipeline using the official google-genai SDK:

  Agent A (Material Classifier)
      ↓  A2A handoff (structured list)
  Agent B (Architectural Maker)
      ↓  A2A handoff (upcycle blueprints markdown)
  Agent C (Regional Sustainability Auditor)  ←  MCP Tool: query_local_registry()

Each agent uses the model defined in `_MODEL_ID` and follows a stateful workflow loop
where outputs are validated before handoff to the next agent.

Architecture:
  User Input → Security Scan → Agent A → Agent B → Agent C → Dashboard
"""

import json
import os
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Day 1 Concept: Foundational API Configuration
# ---------------------------------------------------------------------------
_MODEL_ID = "gemini-3.1-flash-lite"
_KNOWLEDGE_BASE_PATH = Path(__file__).parent / "local_waste_rules.json"


def _get_client() -> genai.Client:
    """Initialize the google-genai client with the user's API key.

    # Day 1 Concept: Secure API Key Management via Environment Variables
    All API configurations strictly reference os.environ.get("GEMINI_API_KEY").
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY environment variable is not set. "
            "Please set it before running EcoWatcher.\n"
            "  Windows:   set GEMINI_API_KEY=your-key-here\n"
            "  Linux/Mac: export GEMINI_API_KEY=your-key-here"
        )
    return genai.Client(api_key=api_key)


# ---------------------------------------------------------------------------
# Day 2 Concept: MCP Local Tool Binding — Knowledge Base Query Function
# ---------------------------------------------------------------------------
def query_local_registry(material: str) -> dict:
    """MCP Tool: Query the local municipal waste rules registry.

    # Day 2 Concept: MCP Local Tool Binding
    # This function is registered as an explicit tool binding for Agent C.
    # It reads from local_waste_rules.json and returns grounded, verified
    # civic data — ensuring Agent C's outputs are non-hallucinated.

    Args:
        material: The waste material name to look up (e.g., "Glass Jars").

    Returns:
        A dictionary containing the verified municipal data for the material,
        or an error message if the material is not found in the registry.
    """
    try:
        with open(_KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)

        waste_db = registry.get("waste_registry", {})

        # --- Exact match first ---
        if material in waste_db:
            return {
                "status": "FOUND",
                "material": material,
                "data": waste_db[material],
            }

        # --- Case-insensitive fuzzy match ---
        material_lower = material.lower().strip()
        for key, value in waste_db.items():
            if material_lower in key.lower() or key.lower() in material_lower:
                return {
                    "status": "FOUND",
                    "material": key,
                    "data": value,
                }

        # --- Not found ---
        available = list(waste_db.keys())
        return {
            "status": "NOT_FOUND",
            "material": material,
            "message": f"Material '{material}' not found in local registry.",
            "available_materials": available,
        }

    except FileNotFoundError:
        return {
            "status": "ERROR",
            "message": f"Knowledge base file not found at {_KNOWLEDGE_BASE_PATH}",
        }
    except json.JSONDecodeError as e:
        return {
            "status": "ERROR",
            "message": f"Failed to parse knowledge base JSON: {e}",
        }


# ---------------------------------------------------------------------------
# Day 3 Concept: Agent Pipeline Result Data Models
# ---------------------------------------------------------------------------
@dataclass
class AgentResult:
    """Result from a single agent in the pipeline."""
    agent_name: str = ""
    output: str = ""
    success: bool = False
    latency_ms: float = 0.0
    error: Optional[str] = None


@dataclass
class PipelineResult:
    """Aggregated result from the full pipeline run."""
    agent_a_result: Optional[AgentResult] = None
    agent_b_result: Optional[AgentResult] = None
    agent_c_result: Optional[AgentResult] = None
    agent_d_result: Optional[AgentResult] = None
    total_latency_ms: float = 0.0
    materials_extracted: List[str] = field(default_factory=list)
    pipeline_success: bool = False

# ---------------------------------------------------------------------------
# API Quota Handling
# ---------------------------------------------------------------------------
import re
def _generate_with_retry(client: genai.Client, model: str, contents: Any, config: types.GenerateContentConfig, max_retries: int = 3) -> Any:
    """Helper to catch 429 RESOURCE_EXHAUSTED errors and retry after sleeping."""
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                if attempt < max_retries - 1:
                    delay = 15.0 # Default wait
                    # The error usually says: "Please retry in 13.67s."
                    match = re.search(r"retry in ([\d\.]+)s", error_str)
                    if match:
                        delay = float(match.group(1)) + 1.0 # Add 1s buffer
                    else:
                        delay = 15.0 * (2 ** attempt) # Exponential backoff
                    print(f"[⚠️ Quota Hit] Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
            raise # If it's not a 429 or we ran out of retries, throw it up
# ---------------------------------------------------------------------------
# Day 3 Concept: ADK Multi-Agent Handoff Loop — Agent A
# Agent A: The Material Classifier
# ---------------------------------------------------------------------------
def _run_agent_a(client: genai.Client, sanitized_input: str) -> AgentResult:
    """Agent A — The Material Classifier.

    # Day 3 Concept: ADK Agent A — Textual Intake Gateway
    # Uses the configured GenAI model to parse unstructured waste descriptions into
    # a standardized Python list of isolated material objects.

    This agent is the entry point of the A2A handoff graph.
    It accepts unstructured user trash strings, extracts discrete items,
    and outputs a structured JSON array for Agent B.

    Args:
        client: Initialized google-genai Client.
        sanitized_input: Pre-processed (security-scanned) user text.

    Returns:
        AgentResult with the extracted materials list as JSON string.
    """
    start = time.perf_counter()

    # Day 3 Concept: Agent System Prompt — Role & Output Contract
    system_prompt = """You are Agent A — The Material Classifier in the EcoWatcher pipeline.

YOUR ROLE: Parse unstructured waste/trash descriptions into a clean, standardized list.

INSTRUCTIONS:
1. Read the user's text describing their waste items.
2. Extract every distinct waste material or object mentioned.
3. Normalize each item name to a concise, standard form.
4. Map items to the closest matching category from this known set when possible:
   - "Glass Jars"
   - "Cardboard Boxes"
   - "Broken Electronics"
   - "Cotton Fabrics"
5. If an item clearly matches one of the above, use the exact category name.
6. If an item does not match, keep its cleaned-up name as-is.

OUTPUT FORMAT — You MUST output ONLY a valid JSON object with this exact structure:
{"materials": ["Item 1", "Item 2", "Item 3"]}

Do NOT include any explanation, markdown, or extra text. ONLY the JSON object."""

    try:
        response = _generate_with_retry(
            client=client,
            model=_MODEL_ID,
            contents=sanitized_input,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,  # Low temperature for deterministic classification
                max_output_tokens=1024,
            ),
        )

        elapsed = (time.perf_counter() - start) * 1000.0
        output_text = response.text.strip()

        return AgentResult(
            agent_name="Agent A — Material Classifier",
            output=output_text,
            success=True,
            latency_ms=round(elapsed, 2),
        )

    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000.0
        return AgentResult(
            agent_name="Agent A — Material Classifier",
            output="",
            success=False,
            latency_ms=round(elapsed, 2),
            error=f"{type(e).__name__}: {e}",
        )


# ---------------------------------------------------------------------------
# Day 3 Concept: ADK Multi-Agent Handoff Loop — Agent B
# Agent B: The Architectural Maker
# ---------------------------------------------------------------------------
def _run_agent_b(client: genai.Client, materials_json: str) -> AgentResult:
    """Agent B — The Architectural Maker.

    # Day 3 Concept: ADK Agent B — Upcycling Design Generator
    # Receives the structured material list from Agent A (A2A handoff)
    # and generates detailed upcycling blueprints in Markdown format.

    Args:
        client: Initialized google-genai Client.
        materials_json: JSON string from Agent A containing the materials list.

    Returns:
        AgentResult with Markdown upcycling blueprints.
    """
    start = time.perf_counter()

    # Day 3 Concept: Agent B System Prompt — Creative Design Generation
    system_prompt = """You are Agent B — The Architectural Maker in the EcoWatcher pipeline.

YOUR ROLE: Generate creative, practical upcycling design blueprints for waste materials.

INSTRUCTIONS:
1. You receive a JSON list of waste materials from Agent A.
2. For EACH material, generate a detailed upcycling blueprint with:
   - A creative project title
   - Required tools and additional materials
   - Step-by-step instructions (5-7 steps)
   - Estimated difficulty level (Beginner / Intermediate / Advanced)
   - Environmental impact note

OUTPUT FORMAT: Well-structured Markdown with clear headings for each material.
Use ## for material headings, ### for sub-sections, and numbered lists for steps.
Make the output visually appealing and informative.
Focus on the REUSE strategy of the 3Rs (Reduce, Reuse, Recycle)."""

    user_prompt = f"""Here is the classified waste material list from Agent A (upstream handoff):

{materials_json}

Generate detailed upcycling blueprints for each material listed above.
Focus on creative, practical, and environmentally responsible reuse strategies."""

    try:
        response = _generate_with_retry(
            client=client,
            model=_MODEL_ID,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,  # Higher creativity for design generation
                max_output_tokens=4096,
            ),
        )

        elapsed = (time.perf_counter() - start) * 1000.0
        output_text = response.text.strip()

        return AgentResult(
            agent_name="Agent B — Architectural Maker",
            output=output_text,
            success=True,
            latency_ms=round(elapsed, 2),
        )

    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000.0
        return AgentResult(
            agent_name="Agent B — Architectural Maker",
            output="",
            success=False,
            latency_ms=round(elapsed, 2),
            error=f"{type(e).__name__}: {e}",
        )


# ---------------------------------------------------------------------------
# Day 3 Concept: ADK Multi-Agent Handoff Loop — Agent C
# Day 2 Concept: MCP Local Tool Binding — Agent C Tool Registration
# Agent C: The Regional Sustainability Auditor
# ---------------------------------------------------------------------------
def _run_agent_c(
    client: genai.Client,
    materials_list: List[str],
    agent_b_output: str,
) -> AgentResult:
    """Agent C — The Regional Sustainability Auditor.

    # Day 3 Concept: ADK Agent C — MCP-Grounded Verification Agent
    # Day 2 Concept: MCP Local Tool Binding — query_local_registry()
    #
    # This agent implements the mandatory MCP tool requirement.
    # It receives query_local_registry as an explicit tool binding,
    # uses it to look up VERIFIED municipal data from local_waste_rules.json,
    # and cross-references Agent B's suggestions with strict civic constraints.
    #
    # Architecture: Agent C calls the MCP tool for EACH material, then
    # generates a compliance audit report that overwrites any hallucinated
    # processing data with verified local rules.

    Args:
        client: Initialized google-genai Client.
        materials_list: Python list of material names from Agent A.
        agent_b_output: The upcycling blueprints Markdown from Agent B.

    Returns:
        AgentResult with the verified sustainability audit report.
    """
    start = time.perf_counter()

    # Day 3 Concept: Agent C System Prompt — Auditor Role with MCP Grounding
    system_prompt = """You are Agent C — The Regional Sustainability Auditor in the EcoWatcher pipeline.

YOUR ROLE: Audit and verify upcycling suggestions using VERIFIED local municipal data.

# Day 2 Concept: MCP Local Tool Binding — Grounded Verification
You have access to the query_local_registry() tool which reads local waste rules from the registry.
This tool represents GROUND TRUTH. You MUST invoke query_local_registry(material) for EACH material in the materials list or Agent B's suggestions.

CRITICAL RULES:
1. Cross-reference Agent B's upcycling suggestions against the verified municipal data returned by the query_local_registry tool.
2. If Agent B suggested any processing steps that CONFLICT with local municipal rules,
   flag them and provide the CORRECT procedure from the verified registry.
3. Always include the official municipal disposal action for each material.
4. Always include the verified toxicity hazard level and any safety warnings.
5. If a material was NOT FOUND in the local registry, clearly state that no verified
   local data is available and recommend contacting municipal services.

OUTPUT FORMAT: Well-structured Markdown with:
- ## heading for each material
- ### Official Municipal Protocol (from verified MCP data)
- ### Toxicity & Safety Assessment (from verified MCP data)
- ### Compliance Notes (any corrections to Agent B's suggestions)
- Use ⚠️ emoji for warnings and ✅ for compliant items.

Focus on the RECYCLE strategy of the 3Rs and strict civic compliance."""

    user_prompt = f"""AUDIT REQUEST — Cross-reference and verify the following:

--- MATERIALS LIST ---
{materials_list}

--- AGENT B's UPCYCLING SUGGESTIONS (to be audited) ---
{agent_b_output}

For each material in the list, please call the query_local_registry tool to retrieve local rules and produce the compliance audit report."""

    try:
        response = _generate_with_retry(
            client=client,
            model=_MODEL_ID,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=[query_local_registry],
                temperature=0.2,  # Low temperature for factual audit
                max_output_tokens=4096,
            ),
        )

        elapsed = (time.perf_counter() - start) * 1000.0
        output_text = response.text.strip()

        return AgentResult(
            agent_name="Agent C — Regional Sustainability Auditor",
            output=output_text,
            success=True,
            latency_ms=round(elapsed, 2),
        )

    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000.0
        return AgentResult(
            agent_name="Agent C — Regional Sustainability Auditor",
            output="",
            success=False,
            latency_ms=round(elapsed, 2),
            error=f"{type(e).__name__}: {e}",
        )


# ---------------------------------------------------------------------------
# Day 3 Concept: ADK Multi-Agent Pipeline Orchestrator
# ---------------------------------------------------------------------------
def _parse_materials_from_agent_a(agent_a_output: str) -> List[str]:
    """Parse the JSON materials list from Agent A's output.

    # Day 3 Concept: A2A Handoff — Structured Payload Parsing
    Handles edge cases like markdown code fences around JSON.

    Args:
        agent_a_output: Raw text output from Agent A.

    Returns:
        Python list of material name strings.
    """
    text = agent_a_output.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (the fences)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict) and "materials" in parsed:
            return parsed["materials"]
        elif isinstance(parsed, list):
            return parsed
        else:
            return [str(parsed)]
    except json.JSONDecodeError:
        # Fallback: try to extract a list from the text
        # Look for quoted strings
        import re
        matches = re.findall(r'"([^"]+)"', text)
        if matches:
            return matches
        # Last resort: split by commas or newlines
        return [item.strip() for item in text.replace("\n", ",").split(",") if item.strip()]


def _run_agent_d(client: genai.Client, materials_list: List[str], location: str) -> AgentResult:
    """Agent D: Uses Google Search tool to find local scrap dealers.

    # Agent D leverages Google Search Grounding to fetch live real-world data
    # for the user's specific location.

    Args:
        client: Initialized google-genai Client.
        materials_list: Python list of material names.
        location: User-provided location string.

    Returns:
        AgentResult with local dealer information.
    """
    start = time.perf_counter()

    system_prompt = """You are Agent D — The Local Logistics Coordinator.

YOUR ROLE: Find real-world scrap dealers, electronic waste recycling centers, or specialized disposal facilities near the user's location that accept their materials.

CRITICAL RULES:
1. You MUST use the google_search tool to find real, currently operating businesses in the provided location.
2. For each material type, list at least one specific place if possible.
3. Provide the business name, address, and a brief note on what they accept.
4. If no specific places are found, provide general advice for that location (e.g., municipal dump info).
5. Output in clean Markdown format with ## headers for each location.
"""

    user_prompt = f"""Find scrap dealers and specialized recycling centers near {location} that accept the following materials:
{materials_list}
"""

    try:
        # First attempt: Try with Google Search Grounding
        response = _generate_with_retry(
            client=client,
            model=_MODEL_ID,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                tools=[{"google_search": {}}],  # Native Google Search Grounding
                temperature=0.3,
            ),
        )
        
        elapsed = (time.perf_counter() - start) * 1000.0
        output_text = response.text.strip()
        return AgentResult(
            agent_name="Agent D — Local Finder",
            output=output_text,
            success=True,
            latency_ms=round(elapsed, 2),
        )

    except Exception as search_err:
        print(f"[⚠️ Agent D] Search Grounding failed ({search_err}). Falling back to pre-trained knowledge...")
        try:
            # Fallback attempt: Try WITHOUT Google Search Grounding
            fallback_prompt = system_prompt.replace(
                "You MUST use the google_search tool", 
                "You do not have search access, rely on your general knowledge to suggest generic types of places"
            )
            response = _generate_with_retry(
                client=client,
                model=_MODEL_ID,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=fallback_prompt,
                    # NO tools provided here to avoid the search quota
                    temperature=0.5,
                ),
            )
            elapsed = (time.perf_counter() - start) * 1000.0
            output_text = response.text.strip()
            
            # Prepend a notice that this is a fallback result
            output_text = "> *Note: Live web search quota was exhausted. These are generic recommendations based on AI knowledge.*\n\n" + output_text
            
            return AgentResult(
                agent_name="Agent D — Local Finder",
                output=output_text,
                success=True,
                latency_ms=round(elapsed, 2),
            )
            
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000.0
            return AgentResult(
                agent_name="Agent D — Local Finder",
                output="",
                success=False,
                latency_ms=round(elapsed, 2),
                error=f"{type(e).__name__}: {e}",
            )


def run_pipeline(sanitized_input: str, location: str = "") -> PipelineResult:
    """Execute the full EcoWatcher pipeline.

    # Day 3 Concept: ADK Multi-Agent Handoff Loop — Full Pipeline
    # Architecture: Agent A → Agent B → Agent C → Agent D
    #
    # Each agent's output is validated before handoff to the next agent.
    # The pipeline collects latency metrics and error states for the
    # operational Watcher Shield dashboard.

    Args:
        sanitized_input: The security-scanned user input (from security_guardrails.py).

    Returns:
        PipelineResult with all three agent results and aggregate metrics.
    """
    pipeline_start = time.perf_counter()
    result = PipelineResult()

    # --- Initialize GenAI client ---
    # Day 1 Concept: API Client Initialization
    client = _get_client()

    # ===================================================================
    # STAGE 1: Agent A — Material Classification
    # Day 3 Concept: ADK Agent A Execution
    # ===================================================================
    result.agent_a_result = _run_agent_a(client, sanitized_input)

    if not result.agent_a_result.success:
        result.total_latency_ms = (time.perf_counter() - pipeline_start) * 1000.0
        return result

    # Day 3 Concept: A2A Handoff — Agent A → Agent B
    materials_list = _parse_materials_from_agent_a(result.agent_a_result.output)
    result.materials_extracted = materials_list

    if not materials_list:
        result.agent_a_result.error = "No materials could be extracted from Agent A's output."
        result.total_latency_ms = (time.perf_counter() - pipeline_start) * 1000.0
        return result

    # ===================================================================
    # STAGE 2: Agent B — Upcycling Blueprint Generation
    # Day 3 Concept: ADK Agent B Execution with A2A Payload
    # ===================================================================
    result.agent_b_result = _run_agent_b(client, result.agent_a_result.output)

    if not result.agent_b_result.success:
        result.total_latency_ms = (time.perf_counter() - pipeline_start) * 1000.0
        return result

    # ===================================================================
    # STAGE 3: Agent C — MCP-Grounded Sustainability Audit
    # Day 3 Concept: ADK Agent C Execution with MCP Tool Binding
    # Day 2 Concept: MCP Tool Invocation via query_local_registry()
    # ===================================================================
    result.agent_c_result = _run_agent_c(
        client, materials_list, result.agent_b_result.output
    )

    # ===================================================================
    # STAGE 4: Agent D — Local Scrap Dealer Search (Google Search)
    # ===================================================================
    if location:
        result.agent_d_result = _run_agent_d(client, materials_list, location)

    # --- Finalize pipeline ---
    result.total_latency_ms = round(
        (time.perf_counter() - pipeline_start) * 1000.0, 2
    )
    result.pipeline_success = all([
        result.agent_a_result and result.agent_a_result.success,
        result.agent_b_result and result.agent_b_result.success,
        result.agent_c_result and result.agent_c_result.success,
        (not location) or (result.agent_d_result and result.agent_d_result.success)
    ])

    return result


# ---------------------------------------------------------------------------
# Day 5 Concept: CLI Execution Pipeline (for Video Demo)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 70)
    print("EcoWatcher — Multi-Agent Pipeline CLI Test")
    print("=" * 70)

    test_input = (
        "I cleaned out my garage and found: three old mason jars, "
        "a huge pile of Amazon shipping boxes, a broken Dell laptop "
        "with a cracked screen, and a bag of old cotton t-shirts "
        "that are too stained to donate."
    )

    print(f"\n[INPUT]\n{test_input}\n")
    print("[RUNNING PIPELINE...]\n")

    try:
        pipeline_result = run_pipeline(test_input)

        print(f"[PIPELINE SUCCESS]: {pipeline_result.pipeline_success}")
        print(f"[TOTAL LATENCY]: {pipeline_result.total_latency_ms} ms")
        print(f"[MATERIALS EXTRACTED]: {pipeline_result.materials_extracted}")

        if pipeline_result.agent_a_result:
            print(f"\n--- Agent A ({pipeline_result.agent_a_result.latency_ms} ms) ---")
            print(pipeline_result.agent_a_result.output[:500])

        if pipeline_result.agent_b_result:
            print(f"\n--- Agent B ({pipeline_result.agent_b_result.latency_ms} ms) ---")
            print(pipeline_result.agent_b_result.output[:500])

        if pipeline_result.agent_c_result:
            print(f"\n--- Agent C ({pipeline_result.agent_c_result.latency_ms} ms) ---")
            print(pipeline_result.agent_c_result.output[:500])

    except Exception as e:
        print(f"[PIPELINE ERROR]: {e}")
        traceback.print_exc()

    print("\n" + "=" * 70)
