"""Script to generate a 4-page factual sample PDF for Study Assistant evaluation."""

from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


def generate_sample_pdf(output_path: Path) -> Path:
    """Generate a 4-page academic notes PDF covering 4 distinct computer science topics."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "PageTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=12,
    )
    subtitle_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=8,
    )

    story = []

    # ==========================================
    # PAGE 1: Machine Learning Basics
    # ==========================================
    story.append(Paragraph("Lecture Notes: Machine Learning Basics", title_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. Fundamental Learning Paradigms", subtitle_style))
    story.append(
        Paragraph(
            "Machine learning algorithms build mathematical models from sample data to make predictions "
            "or decisions without being explicitly programmed. In supervised learning, the training set consists "
            "of input features paired with ground-truth targets, enabling regression for continuous outputs and "
            "classification for discrete labels. Conversely, unsupervised learning discovers hidden patterns or cluster "
            "structures within unlabeled datasets using methods like k-means clustering and principal component analysis.",
            body_style,
        )
    )

    story.append(Paragraph("2. Overfitting and Regularization Techniques", subtitle_style))
    story.append(
        Paragraph(
            "Overfitting occurs when an algorithm models the noise and statistical idiosyncrasies of the training data "
            "rather than the underlying general trend, yielding high training accuracy but poor generalization to test sets. "
            "Regularization mitigates overfitting by penalizing complex hypothesis weights. L1 regularization (Lasso) adds "
            "the absolute value of weights to the cost function, promoting parameter sparsity by driving irrelevant weights to zero. "
            "L2 regularization (Ridge) adds the squared magnitude of coefficients, shrinking weights smoothly toward zero without exact elimination.",
            body_style,
        )
    )

    story.append(Paragraph("3. The Bias-Variance Tradeoff", subtitle_style))
    story.append(
        Paragraph(
            "The bias-variance tradeoff is a central theoretical dilemma in statistical learning. Bias measures erroneous "
            "assumptions made by the learning algorithm; high bias leads to underfitting where models fail to capture complex relationships. "
            "Variance measures model sensitivity to slight fluctuations in training sets; high variance causes overfitting where minor "
            "sample variations alter predicted functions significantly. The total expected generalization error equals the sum of squared bias, "
            "variance, and irreducible noise.",
            body_style,
        )
    )

    story.append(Paragraph("4. Optimization and Model Validation", subtitle_style))
    story.append(
        Paragraph(
            "Gradient descent is an iterative first-order optimization algorithm that minimizes empirical loss functions by computing "
            "partial derivatives with respect to parameters and taking steps proportional to the negative gradient scaled by the learning rate. "
            "To accurately evaluate model performance before deployment, practitioners employ k-fold cross-validation. The dataset is split "
            "into k equal partitions; the model trains on k-1 subsets and validates on the remaining fold, repeating k times to compute a robust average metric.",
            body_style,
        )
    )

    story.append(PageBreak())

    # ==========================================
    # PAGE 2: Databases and SQL
    # ==========================================
    story.append(Paragraph("Lecture Notes: Databases and SQL Architecture", title_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. The Relational Model and Schemas", subtitle_style))
    story.append(
        Paragraph(
            "The relational database model organizes data into two-dimensional tables termed relations, composed of rows "
            "(tuples) and columns (attributes). Each tuple represents a single record identified uniquely by a primary key, "
            "while foreign keys enforce referential integrity across relational boundaries. Schemas specify table constraints, data types, "
            "and default values to prevent structural corruption.",
            body_style,
        )
    )

    story.append(Paragraph("2. ACID Properties of Transactions", subtitle_style))
    story.append(
        Paragraph(
            "Database transaction management relies on four fundamental ACID properties to guarantee reliability. "
            "Atomicity ensures that all operations in a transaction execute completely or roll back entirely with no partial state. "
            "Consistency guarantees that database state transitions preserve all defined schema rules and integrity constraints. "
            "Isolation dictates that concurrent transaction executions do not interfere with one another, preventing dirty reads through concurrency locks. "
            "Durability guarantees that once a transaction commits, its modifications persist permanently even across power failures.",
            body_style,
        )
    )

    story.append(Paragraph("3. Indexing Structures and B-Trees", subtitle_style))
    story.append(
        Paragraph(
            "Database indexes dramatically accelerate query search speeds by transforming full table scans of O(N) complexity into logarithmic "
            "time lookups of O(log N). The most prevalent indexing data structure is the balanced B-Tree (or B+ Tree), which maintains sorted "
            "keys across balanced hierarchical nodes, providing stable performance for both exact equality matches and range-based queries.",
            body_style,
        )
    )

    story.append(Paragraph("4. Normalization and SQL Relational Joins", subtitle_style))
    story.append(
        Paragraph(
            "Database normalization decomposes relations to eliminate insertion, update, and deletion anomalies while reducing duplicate storage. "
            "First Normal Form (1NF) demands atomic attribute values; Second Normal Form (2NF) eliminates partial key functional dependencies; "
            "and Third Normal Form (3NF) removes transitive dependencies. In SQL queries, relational joins recombine partitioned tables: "
            "an INNER JOIN produces only records matching both join conditions, whereas a LEFT OUTER JOIN preserves all rows from the left table "
            "supplemented with null values when no matching right records exist.",
            body_style,
        )
    )

    story.append(PageBreak())

    # ==========================================
    # PAGE 3: Operating System Scheduling
    # ==========================================
    story.append(Paragraph("Lecture Notes: Operating System Process Scheduling", title_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. Process Lifecycle and Process Control Blocks", subtitle_style))
    story.append(
        Paragraph(
            "A process is a program in active execution requiring memory space, registers, and system resources. An operating system "
            "tracks each process across distinct lifecycle states: New during creation, Ready waiting in line for CPU assignment, Running executing instructions, "
            "Waiting or Blocked suspended pending I/O operations, and Terminated upon completion. The kernel maintains process state using a dedicated "
            "Process Control Block (PCB) containing the program counter, CPU registers, memory limits, and open file descriptors.",
            body_style,
        )
    )

    story.append(Paragraph("2. CPU Scheduling Algorithms", subtitle_style))
    story.append(
        Paragraph(
            "The CPU scheduler determines which ready process claims the processor next to maximize throughput and minimize response latency. "
            "First-Come First-Served (FCFS) schedules processes chronologically but suffers from the convoy effect when lengthy tasks delay brief jobs. "
            "Shortest Job First (SJF) minimizes average waiting time but risks starvation for elongated computational jobs. "
            "Round Robin (RR) scheduling allocates a fixed duration called a time quantum to each ready process in cyclic succession, ensuring preemptive "
            "fairness ideal for interactive time-sharing systems.",
            body_style,
        )
    )

    story.append(Paragraph("3. Context Switching Overhead", subtitle_style))
    story.append(
        Paragraph(
            "A context switch occurs when the OS kernel suspends one active thread and loads another. The kernel saves CPU registers, pointer addresses, "
            "and execution flags into the outgoing PCB and restores equivalent registers from the incoming PCB. Because context switching consumes CPU cycles "
            "without advancing user computation, time quanta in Round Robin must be tuned carefully to avoid excessive switching overhead.",
            body_style,
        )
    )

    story.append(Paragraph("4. Deadlocks and Virtual Memory Paging", subtitle_style))
    story.append(
        Paragraph(
            "A deadlock occurs when multiple processes are permanently halted because each holds a resource needed by another. Coffman identified four "
            "simultaneous conditions necessary for deadlock: Mutual Exclusion (non-shareable resources), Hold and Wait (processes holding allocated resources while requesting more), "
            "No Preemption (resources cannot be forcibly taken), and Circular Wait (a closed loop of waiting processes). "
            "In modern virtual memory architectures, logical address space is divided into fixed-size chunks called pages mapped to physical frames. "
            "When a process accesses a page not resident in RAM, a hardware interrupt triggers a page fault, prompting the OS to retrieve the page from disk via LRU replacement.",
            body_style,
        )
    )

    story.append(PageBreak())

    # ==========================================
    # PAGE 4: Computer Networks
    # ==========================================
    story.append(Paragraph("Lecture Notes: Computer Networks and Architecture", title_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. The OSI Seven-Layer Reference Model", subtitle_style))
    story.append(
        Paragraph(
            "The Open Systems Interconnection (OSI) model standardizes network communication into seven hierarchical abstraction layers. "
            "The Physical Layer transmits raw bit streams over hardware media; the Data Link Layer manages node-to-node framing and MAC addressing; "
            "the Network Layer directs packets through routing algorithms and IP addressing; the Transport Layer ensures end-to-end reliability and flow control; "
            "the Session Layer establishes dialog connections; the Presentation Layer handles data encryption and compression; "
            "and the Application Layer provides protocols directly for user software services.",
            body_style,
        )
    )

    story.append(Paragraph("2. Transport Protocols and the TCP Three-Way Handshake", subtitle_style))
    story.append(
        Paragraph(
            "The transport layer is dominated by TCP and UDP protocols. TCP (Transmission Control Protocol) is connection-oriented, delivering "
            "guaranteed, in-order packet streams through flow control, congestion avoidance, and sequence acknowledgments. Connection initiation requires a "
            "three-way handshake: the client transmits a SYN segment with an initial sequence number; the server responds with a SYN-ACK acknowledging the client's SYN; "
            "and the client replies with an ACK, establishing the bidirectional connection. In contrast, UDP (User Datagram Protocol) is connectionless and lightweight, "
            "sacrificing packet delivery guarantees to achieve low latency in real-time gaming, VoIP, and video streaming.",
            body_style,
        )
    )

    story.append(Paragraph("3. IP Addressing and Subnet Routing", subtitle_style))
    story.append(
        Paragraph(
            "Network devices are addressed via IPv4 (32-bit addresses formatted as dotted-decimal notation) or IPv6 (128-bit hexadecimal strings). "
            "Subnet masks delineate network prefixes from individual host portions, allowing hierarchical routing across autonomous systems. "
            "Routers employ routing protocols such as OSPF for interior gateway routing and BGP (Border Gateway Protocol) for exchanging reachability across the global Internet backbone.",
            body_style,
        )
    )

    story.append(Paragraph("4. DNS Resolution and Web Application Protocols", subtitle_style))
    story.append(
        Paragraph(
            "The Domain Name System (DNS) translates human-readable domain names into numerical IP addresses. When a user requests a URL, a recursive resolver queries "
            "Root nameservers, followed by Top-Level Domain (TLD) servers (e.g., .com or .org), and finally Authoritative DNS servers holding the definitive A or AAAA records. "
            "Web traffic communicates over HTTP and HTTPS; HTTPS secures plain-text HTTP by encrypting payloads using Transport Layer Security (TLS), preventing eavesdropping "
            "and man-in-the-middle tampering through public-key cryptography and digital certificates.",
            body_style,
        )
    )

    doc.build(story)
    return output_path


if __name__ == "__main__":
    target = Path("data") / "sample" / "sample_notes.pdf"
    generate_sample_pdf(target)
    print(f"Sample PDF successfully created at: {target}")
