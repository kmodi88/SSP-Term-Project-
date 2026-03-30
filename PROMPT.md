# Prompts Used for KDE Extraction

## Zero-Shot

You are a security analyst. Read the following security requirements document
and identify all Key Data Elements (KDEs). For each KDE, list its name and
the specific requirements that reference it. Return ONLY valid YAML in this
exact format:

element1:
name: <name>
requirements:
- <req1>
- <req2>

Document:
{document_text}

---

## Few-Shot

You are a security analyst. Below is an example of identifying Key Data
Elements (KDEs) from a security requirements document.

Example input: 'Passwords must be at least 8 characters. Passwords must not
be reused within 12 months.'

Example output:
element1:
name: Password
requirements:
- Passwords must be at least 8 characters
- Passwords must not be reused within 12 months

Now do the same for this document. Return ONLY valid YAML:

Document:
{document_text}

---

## Chain-of-Thought

You are a security analyst. Follow these steps to identify Key Data Elements
(KDEs) from a security requirements document:

Step 1: Read the full document carefully.
Step 2: Identify all distinct data entities mentioned (e.g., passwords, user
accounts, logs).
Step 3: For each entity, collect every requirement sentence that references it.
Step 4: Format your findings as valid YAML only, like this:

element1:
name: <name>
requirements:
- <req1>
- <req2>

Document:
{document_text}