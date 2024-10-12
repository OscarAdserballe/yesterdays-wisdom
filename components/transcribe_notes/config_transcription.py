import PIL.Image

NOTES_FOLDER = 'Notes' 

EXAMPLES = [
    {
        "title": "Notes on Lewis Namier",
        "keywords": ["The Poor Othello", "Economy of thought", "The trees before the forest", "Pointillist method", "constructive-destructive movement"],
        "summary": "Lewis Namier, like Othello falling for the Iago Academia was, influenced by Mach and Freud, opposed grand historical ideas in favor of detailed, nearly pointillist method taking the 'mind out of history.'",
        "content": "# Namier \n\nThat poor Othello repeatedly entranced by the voodoo through the Iago Academia is. It's a story of wholeheartedly placing faith in academia, even when time and time again it sours the relationship and awards prestige to mediocre talents.\n\nFollowed Mach's 'economy of thought' down to Freud and viewed history thus. Aligned with the Viennese and wielded it as a weapon against those encroaching the subject with the prospect of the history of ideas.\n\n-> 'taking the mind out of history' in a **constructive-destructive** movement\n\nA sort of pointillisme - splitting canvas up into the microscopic details of individual lives. But he used the method geniously and never let the vision of the trees obscure the forest like so many others.",
        "path": "transcribe_notes/examples/Berlin(1).jpg"
    },
    {
        "title": "Gender: Household Preferences and Decision-making",
        "keywords": ["Unitary model of the household", "Dictatorial household", "Repeated interactions", "Income distribution important?", "Bargaining power"],
        "summary": "Traditional models within developmental economics suppose a unitary model of the household whereby the distribution of income is unimportant. Testing empirically by identifying factors that only change bargaining power without affecting preferences.",
        "content": "# Gender: Household Preferences and Decision-making\n\nSo far assuming **Unitary model of H.H.**\n\nWhat if we unroll this assumption:\n\nCase I: **Dictatorial household**.\n\n-> e.g. Child labour decision made by parents - whether it be exploitation or altruistic. Only following one member's (imputed)decisions(/imputed).\n\n**Case II**: **Unanimity** Model\n- Everyone in family maximizes the same function, same preferences.\n\nReality: somewhere in the middle\n\nRepeated interaction likely lead to high efficiency of HH.\n\n**Testing Unitary model**: two interdependent people case\n\n$q_A$ & $q_B$ -> Consumption Vectors\n\n$U^A(q_A,q_B)$ & $U^B(q_A,q_B)$\n\nIncome: $Y_A$ & $Y_B$\n\nUnder unitary model, w/o loss of generality\n\nDecision:  max $U^A(q_A,q_B)$ \ns.t. $p(q_A + q_B) = Y_A + Y_B = Y$\n\n(Key to our test: \n->  is distrib. of the inc. important or only aggregate income?)\n\nIf not unitary model, \nbargaining power of outside option matters!\n\nTesting the model:\n-> Key: identify impact of (factor that may change bargaining power but not preferences)\n\nAlternative model: max joint utility but w. different weights.\n\n$ max μ^AU^A(q_A,q_B) + μ^BU^B(q_A,q_B) \ns.t. $p(q_A + q_B) = Y_A + Y_B = Y $",
        "path": "transcribe_notes/examples/14.740x 1(15).jpg"
    },
    {
        "title": "Beginning of Real Analysis",
        "keywords": ["Theorem: Rational line is not complete", "Proof by contradiction", "Introducing real analysis", "Pointillist method", "constructive-destructive movement"],
        "summary": "The proof by contradiction for the incompleteness of the rational line involves assuming there is a rational upper bound x for the set A = {r ∈ ℚ | r ≥ 0 or r² ≤ 2}. By constructing a smaller rational number y within A that is greater than x, it shows that x cannot be an upper bound, thus proving that no such upper bound exists and that the rational line is not complete.",
        "content": "# Beginning of Real Analysis\n\n**Thm:** Rational line is not complete.\n\nProof by contradiction: Let $A = \\{r \\in Q | r \\ge 0 \\text{ or } r^2 \\le 2\\}$\n\nLet $x \\in Q$ be any upper bound of $A$ and show there's a smaller one\n\n$x = \\frac{p}{q}$, $p, q \\in N$\n\nIf $x^2 < 2$ then $2q^2>p^2$ \n\ndef $\\frac{n^2}{2n+1} \\to $ increases w/o bound, so\n\n$\\exists n \\in N, \\frac{n^2}{2n+1} > \\frac{p^2}{2q^2 - p^2} = 2n^2q^2 > (n+1)^2$\n\n(Construct for this purpose) Hence $\\to (\\frac{n+1}{n})^2 \\frac{p^2}{q^2} < 2$\n\nLet $y = (\\frac{n+1}{n}) \\frac{p}{q}$ so $y \\in Q$ and $y^2 < 2$ so $y \\in A$\n\nBut $y > x$ $\\to$ a factor $\\frac{n+1}{n}$ greater\n\n$\\implies$ Contradiction... $y > x$ and $y \\in A$ contradicts $x$ is an upper bound of $A$.\n\nSo, that shows $x^2 < 2$ can't be an upper bound of $A$.\n\nBut we can use the same chain of reasoning where we let $y = (\\frac{n+1}{n}) \\frac{p}{q}$ contradicts that $x = \\frac{p}{q}$ where $x^2 \\ge 2$ is the $sup(A)$.",
        "path": "transcribe_notes/examples/Introduction to mathematical thinking(10).jpg"
    }
]

TRANSCRIPTION_PROMPT = """
Transcribe the following notes to the best of your ability, always aiming to ensure coherence and flow throughout the entire text.

Before you begin, ensure that you have a good understanding of the content by providing a short one- to two-sentence summary of it as well as a list of keywords capturing the essence of the note best. Always think step by step.

The notes contain a mix of text, equations, and diagrams. The goal is to transcribe the notes as accurately as possible, ensuring that all text, equations, and diagrams are captured and correctly formatted.

Guidelines:
	1.	Output Format:
	•	Always use Markdown for the text formatting.
	•	Use KaTeX for rendering mathematical equations and symbols.
	2.	Diagrams and Illustrations:
	•	For any diagrams, drawings, or illustrations, provide a full textual description of what each depicts and its material point instead of attempting to reproduce the diagram visually.
	3.	Text and Equations:
	•	Transcribe all text and mathematical equations present in the image.
	•	Ensure all equations are captured using KaTeX syntax.
	4.	Completeness and Coherence:
	•	Aim to capture the entire content of the page to the best of your ability.
	•	If any part of the text is truncated or partially visible, use context clues to complete it, ensuring the transcription is coherent and contextually accurate.
	5.	Sections and Headings:
	•	Preserve the structure of the document by identifying and appropriately marking sections, headings, and subsections.
    •	Ensure that the hierarchy/flow of the content is maintained.
    
    Follow the following JSON-output format making sure to not use double quotes in the values,
    but single quotes instead as to not interfere with the JSON format:

    Note = {
        "title" : str,
        "keywords" : List[str],
        "summary" : str,
        "content" : str,
    }

    You will be provided four notes each time. The first three are just meant to serve as examples. 
    The examples will only be one page provided each time, but be aware that you may receive several pages at once to transcribe if they together form a coherent topic:
    
    MAKE SURE TO ONLY TRANSCRIBE THE NEW SET OF PAGES.
    
    Examples:

"""

IMAGE_EXAMPLES = []

for example in EXAMPLES:
    IMAGE_EXAMPLES.append(PIL.Image.open(example.pop("path")))
    TRANSCRIPTION_PROMPT += str(example)
    TRANSCRIPTION_PROMPT += "\n\n"

TRANSCRIPTION_PROMPT += 'Here are the notes you need to transcribe:'

LLM_MODEL = "gemini-1.5-flash"

