"""
Static mock data for the Research Intelligence Server.

12 papers across 4 domains with internally consistent citation relationships.
Every paper_id referenced in `references` or `cited_by` exists in this dataset.

Domain distribution:
  machine-learning:            4 papers (paper-001 to paper-004)
  natural-language-processing: 3 papers (paper-005 to paper-007)
  distributed-systems:         3 papers (paper-008 to paper-010)
  computer-vision:             2 papers (paper-011 to paper-012)
"""

from research_server.models.domain import Domain, Paper

PAPERS: list[Paper] = [

    # -----------------------------------------------------------------------
    # Machine Learning (4 papers)
    # -----------------------------------------------------------------------

    Paper(
        id="paper-001",
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit"],
        year=2017,
        domain=Domain.MACHINE_LEARNING,
        tags=["transformers", "attention", "sequence-to-sequence", "neural-networks"],
        abstract=(
            "The dominant sequence transduction models are based on complex recurrent or "
            "convolutional neural networks that include an encoder and a decoder. We propose "
            "a new simple network architecture, the Transformer, based solely on attention "
            "mechanisms, dispensing with recurrence and convolutions entirely."
        ),
        citation_count=95000,
        references=[],
        cited_by=["paper-002", "paper-003", "paper-005", "paper-006"],
        full_text=(
            "1. Introduction\n"
            "Recurrent neural networks, long short-term memory and gated recurrent neural "
            "networks in particular, have been firmly established as state of the art approaches "
            "in sequence modelling and transduction problems such as language modelling and "
            "machine translation.\n\n"
            "2. Model Architecture\n"
            "Most competitive neural sequence transduction models have an encoder-decoder "
            "structure. The encoder maps an input sequence of symbol representations to a "
            "sequence of continuous representations.\n\n"
            "3. Attention Mechanisms\n"
            "An attention function can be described as mapping a query and a set of key-value "
            "pairs to an output. We call our particular attention Scaled Dot-Product Attention.\n\n"
            "4. Results\n"
            "On the WMT 2014 English-to-German translation task, the big transformer model "
            "outperforms the best previously reported models by more than 2.0 BLEU."
        ),
    ),

    Paper(
        id="paper-002",
        title="BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        authors=["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
        year=2018,
        domain=Domain.MACHINE_LEARNING,
        tags=["bert", "transformers", "pre-training", "fine-tuning", "nlp"],
        abstract=(
            "We introduce BERT, which stands for Bidirectional Encoder Representations from "
            "Transformers. BERT is designed to pre-train deep bidirectional representations "
            "from unlabeled text by jointly conditioning on both left and right context. "
            "The pre-trained BERT model can be fine-tuned with just one additional output "
            "layer to create state-of-the-art models for a wide range of tasks."
        ),
        citation_count=60000,
        references=["paper-001"],
        cited_by=["paper-003", "paper-005", "paper-006"],
        full_text=(
            "1. Introduction\n"
            "Language model pre-training has been shown to be effective for improving many "
            "natural language processing tasks, including sentence-level tasks such as "
            "natural language inference and token-level tasks such as named entity recognition.\n\n"
            "2. BERT Architecture\n"
            "BERT's model architecture is a multi-layer bidirectional Transformer encoder. "
            "The number of layers is denoted as L, the hidden size as H, and the number "
            "of self-attention heads as A.\n\n"
            "3. Pre-training Tasks\n"
            "We pre-train BERT using two tasks: Masked Language Model (MLM) and Next "
            "Sentence Prediction (NSP). MLM randomly masks input tokens and the objective "
            "is to predict the original vocabulary id based only on context.\n\n"
            "4. Fine-tuning\n"
            "For each task, we plug in the task-specific inputs and outputs into BERT "
            "and fine-tune all parameters end-to-end."
        ),
    ),

    Paper(
        id="paper-003",
        title="Scaling Laws for Neural Language Models",
        authors=["Jared Kaplan", "Sam McCandlish", "Tom Henighan", "Tom B. Brown"],
        year=2020,
        domain=Domain.MACHINE_LEARNING,
        tags=["scaling", "language-models", "compute", "neural-networks"],
        abstract=(
            "We study empirical scaling laws for language model performance on the "
            "cross-entropy loss. The loss scales as a power-law with model size, dataset "
            "size, and the amount of compute used for training, with some trends spanning "
            "more than seven orders of magnitude."
        ),
        citation_count=8000,
        references=["paper-001", "paper-002"],
        cited_by=["paper-004"],
        full_text=(
            "1. Introduction\n"
            "Language models have demonstrated rapid progress across a wide range of natural "
            "language tasks. We investigate the scaling behavior of language model performance, "
            "finding that behaviors can be described by smooth power laws.\n\n"
            "2. Scaling Laws\n"
            "Model performance improves predictably as we scale model size N, dataset size D, "
            "and compute budget C. The relationship follows a power law: L(N) = (Nc/N)^alpha_N.\n\n"
            "3. Optimal Compute Allocation\n"
            "Given a fixed compute budget, there is an optimal model size and number of training "
            "tokens. Larger models trained for fewer steps are more compute-efficient."
        ),
    ),

    Paper(
        id="paper-004",
        title="Chinchilla: Training Compute-Optimal Large Language Models",
        authors=["Jordan Hoffmann", "Sebastian Borgeaud", "Arthur Mensch"],
        year=2022,
        domain=Domain.MACHINE_LEARNING,
        tags=["scaling", "large-language-models", "compute-optimal", "training"],
        abstract=(
            "We investigate the optimal model size and number of tokens for training a "
            "transformer language model under a given compute budget. We find that for "
            "compute-optimal training, model size and number of training tokens should be "
            "scaled equally: for every doubling of model size, training tokens should double."
        ),
        citation_count=4500,
        references=["paper-003"],
        cited_by=[],
        full_text=(
            "1. Introduction\n"
            "Kaplan et al. (2020) proposed that given a fixed FLOPs budget, one should train "
            "a large model on fewer tokens. We revisit this with more rigorous methodology.\n\n"
            "2. Estimating Optimal Tradeoffs\n"
            "We use three approaches to estimate the optimal number of training tokens for a "
            "given compute budget. All three converge: current large language models are "
            "significantly undertrained.\n\n"
            "3. Chinchilla Results\n"
            "Chinchilla, a 70B parameter model trained on 1.4 trillion tokens, uniformly "
            "outperforms Gopher on all downstream evaluation tasks."
        ),
    ),

    # -----------------------------------------------------------------------
    # Natural Language Processing (3 papers)
    # -----------------------------------------------------------------------

    Paper(
        id="paper-005",
        title="GPT-3: Language Models are Few-Shot Learners",
        authors=["Tom B. Brown", "Benjamin Mann", "Nick Ryder", "Melanie Subbiah"],
        year=2020,
        domain=Domain.NATURAL_LANGUAGE_PROCESSING,
        tags=["gpt-3", "few-shot", "in-context-learning", "large-language-models"],
        abstract=(
            "We demonstrate that scaling up language models greatly improves task-agnostic "
            "few-shot performance. We train GPT-3, an autoregressive language model with "
            "175 billion parameters, and test its performance in the few-shot setting without "
            "any gradient updates or fine-tuning."
        ),
        citation_count=35000,
        references=["paper-001", "paper-002"],
        cited_by=["paper-006", "paper-007"],
        full_text=(
            "1. Introduction\n"
            "Recent years have featured a trend towards pre-trained language representations "
            "applied in increasingly flexible and task-agnostic ways.\n\n"
            "2. Approach\n"
            "We follow the same model and architecture as GPT-2, including modified "
            "initialization, pre-normalization, and reversible tokenization, with alternating "
            "dense and locally banded sparse attention patterns.\n\n"
            "3. Results\n"
            "GPT-3 achieves strong performance on many NLP datasets including translation, "
            "question-answering, and tasks requiring on-the-fly reasoning such as arithmetic."
        ),
    ),

    Paper(
        id="paper-006",
        title="Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        authors=["Jason Wei", "Xuezhi Wang", "Dale Schuurmans", "Maarten Bosma"],
        year=2022,
        domain=Domain.NATURAL_LANGUAGE_PROCESSING,
        tags=["chain-of-thought", "reasoning", "prompting", "large-language-models"],
        abstract=(
            "We explore how generating a chain of thought — a series of intermediate reasoning "
            "steps — significantly improves the ability of large language models to perform "
            "complex reasoning. Reasoning abilities emerge naturally in sufficiently large "
            "language models via chain-of-thought prompting."
        ),
        citation_count=12000,
        references=["paper-001", "paper-002", "paper-005"],
        cited_by=["paper-007"],
        full_text=(
            "1. Introduction\n"
            "Scaling alone has not proved sufficient for achieving high performance on "
            "challenging tasks such as arithmetic, commonsense, and symbolic reasoning.\n\n"
            "2. Chain-of-Thought Prompting\n"
            "A chain of thought is a series of short sentences that mimic step-by-step "
            "reasoning. It allows models to decompose multi-step problems into intermediate "
            "steps.\n\n"
            "3. Results\n"
            "Chain-of-thought prompting substantially improves performance across all model "
            "sizes on arithmetic reasoning benchmarks."
        ),
    ),

    Paper(
        id="paper-007",
        title="ReAct: Synergizing Reasoning and Acting in Language Models",
        authors=["Shunyu Yao", "Jeffrey Zhao", "Dian Yu", "Nan Du"],
        year=2023,
        domain=Domain.NATURAL_LANGUAGE_PROCESSING,
        tags=["react", "reasoning", "acting", "agents", "tool-use"],
        abstract=(
            "We explore the use of LLMs to generate both reasoning traces and task-specific "
            "actions in an interleaved manner. Reasoning traces help the model induce, track, "
            "and update action plans, while actions allow it to interface with external "
            "sources to gather additional information."
        ),
        citation_count=5500,
        references=["paper-005", "paper-006"],
        cited_by=[],
        full_text=(
            "1. Introduction\n"
            "A unique feature of human intelligence is the ability to seamlessly combine "
            "task-oriented actions with verbal reasoning to solve complex tasks.\n\n"
            "2. ReAct\n"
            "ReAct prompts LLMs to generate both verbal reasoning traces and actions in "
            "an interleaved fashion, allowing dynamic reasoning to create and adjust plans "
            "while interacting with external environments.\n\n"
            "3. Results\n"
            "ReAct outperforms chain-of-thought reasoning and acting-only baselines on "
            "HotpotQA, Fever, ALFWORLD, and WebShop tasks."
        ),
    ),

    # -----------------------------------------------------------------------
    # Distributed Systems (3 papers)
    # -----------------------------------------------------------------------

    Paper(
        id="paper-008",
        title="MapReduce: Simplified Data Processing on Large Clusters",
        authors=["Jeffrey Dean", "Sanjay Ghemawat"],
        year=2004,
        domain=Domain.DISTRIBUTED_SYSTEMS,
        tags=["mapreduce", "parallel-computing", "large-scale", "fault-tolerance"],
        abstract=(
            "MapReduce is a programming model for processing and generating large data sets. "
            "Users specify a map function that processes key/value pairs to generate "
            "intermediate pairs, and a reduce function that merges all intermediate values "
            "associated with the same key."
        ),
        citation_count=25000,
        references=[],
        cited_by=["paper-009", "paper-010"],
        full_text=(
            "1. Introduction\n"
            "Over the past five years, the authors have implemented hundreds of special-purpose "
            "computations that process large amounts of raw data across thousands of machines.\n\n"
            "2. Programming Model\n"
            "The computation takes a set of input key/value pairs and produces output key/value "
            "pairs via user-defined Map and Reduce functions.\n\n"
            "3. Fault Tolerance\n"
            "The master pings every worker periodically. If no response is received, the "
            "master marks the worker as failed and reschedules its tasks."
        ),
    ),

    Paper(
        id="paper-009",
        title="Raft: In Search of an Understandable Consensus Algorithm",
        authors=["Diego Ongaro", "John Ousterhout"],
        year=2014,
        domain=Domain.DISTRIBUTED_SYSTEMS,
        tags=["raft", "consensus", "distributed-consensus", "fault-tolerance", "replication"],
        abstract=(
            "Raft is a consensus algorithm designed as an alternative to Paxos. It was "
            "designed to be more understandable than Paxos and provides a better foundation "
            "for building practical systems by separating leader election, log replication, "
            "and safety."
        ),
        citation_count=11000,
        references=["paper-008"],
        cited_by=["paper-010"],
        full_text=(
            "1. Introduction\n"
            "Consensus algorithms allow a collection of machines to work as a coherent group "
            "that can survive the failures of some of its members.\n\n"
            "2. Leader Election\n"
            "Raft uses a heartbeat mechanism to trigger leader election. Servers start as "
            "followers and remain so as long as they receive valid RPCs from a leader.\n\n"
            "3. Log Replication\n"
            "Once a leader is elected, it begins servicing client requests. Each request "
            "contains a command to be executed by the replicated state machines."
        ),
    ),

    Paper(
        id="paper-010",
        title="Dynamo: Amazon's Highly Available Key-Value Store",
        authors=["Giuseppe DeCandia", "Deniz Hastorun", "Madan Jampani"],
        year=2007,
        domain=Domain.DISTRIBUTED_SYSTEMS,
        tags=["dynamo", "key-value-store", "availability", "eventual-consistency", "cap-theorem"],
        abstract=(
            "Dynamo is a highly available key-value storage system used by Amazon's core "
            "services. To achieve high availability, Dynamo sacrifices consistency under "
            "certain failure scenarios and uses object versioning with application-assisted "
            "conflict resolution."
        ),
        citation_count=18000,
        references=["paper-008", "paper-009"],
        cited_by=[],
        full_text=(
            "1. Introduction\n"
            "Amazon's platform serves tens of millions of customers using tens of thousands "
            "of servers with strict requirements on performance, reliability, and efficiency.\n\n"
            "2. Design Considerations\n"
            "In many situations it is not clear when a system fails versus when it is slow. "
            "Systems handling large numbers of failures must sacrifice consistency for "
            "availability.\n\n"
            "3. Consistent Hashing\n"
            "Dynamo uses consistent hashing to partition its key space across replicas and "
            "ensure load balancing when nodes join and leave."
        ),
    ),

    # -----------------------------------------------------------------------
    # Computer Vision (2 papers)
    # -----------------------------------------------------------------------

    Paper(
        id="paper-011",
        title="Deep Residual Learning for Image Recognition",
        authors=["Kaiming He", "Xiangyu Zhang", "Shaoqing Ren", "Jian Sun"],
        year=2016,
        domain=Domain.COMPUTER_VISION,
        tags=["resnet", "residual-learning", "deep-learning", "image-classification"],
        abstract=(
            "We present a residual learning framework to ease the training of substantially "
            "deeper networks. We explicitly reformulate layers as learning residual functions "
            "with reference to layer inputs, instead of learning unreferenced functions. "
            "These residual networks are easier to optimize and gain accuracy from "
            "considerably increased depth."
        ),
        citation_count=140000,
        references=[],
        cited_by=["paper-012"],
        full_text=(
            "1. Introduction\n"
            "Deep convolutional neural networks have led to breakthroughs for image "
            "classification. Deeper networks naturally integrate low, mid, and high-level "
            "features in an end-to-end multilayer fashion.\n\n"
            "2. Residual Learning\n"
            "Instead of hoping stacked layers fit a desired mapping H(x), we let layers "
            "fit a residual mapping F(x) := H(x) - x. The original mapping becomes F(x) + x.\n\n"
            "3. Results\n"
            "A 152-layer ResNet is the deepest network ever presented on ImageNet, while "
            "still having lower complexity than VGG nets."
        ),
    ),

    Paper(
        id="paper-012",
        title="An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
        authors=["Alexey Dosovitskiy", "Lucas Beyer", "Alexander Kolesnikov"],
        year=2020,
        domain=Domain.COMPUTER_VISION,
        tags=["vit", "vision-transformer", "image-classification", "transformers"],
        abstract=(
            "While the Transformer architecture has become the standard for NLP, its "
            "applications to computer vision remain limited. We show that a pure transformer "
            "applied directly to sequences of image patches can perform very well on image "
            "classification tasks without relying on CNNs."
        ),
        citation_count=45000,
        references=["paper-011"],
        cited_by=[],
        full_text=(
            "1. Introduction\n"
            "Inspired by Transformer scaling successes in NLP, we apply a standard Transformer "
            "directly to images with the fewest possible modifications, splitting images into "
            "patches and providing linear embeddings as input.\n\n"
            "2. Method\n"
            "We follow the original Transformer as closely as possible. The standard "
            "Transformer receives a 1D sequence of token embeddings as input.\n\n"
            "3. Results\n"
            "Vision Transformers outperform ResNets on all benchmarks when pre-trained on "
            "large datasets such as ImageNet-21k or JFT-300M."
        ),
    ),
]

# Lookup index for O(1) access by paper ID
PAPERS_BY_ID: dict[str, Paper] = {paper.id: paper for paper in PAPERS}