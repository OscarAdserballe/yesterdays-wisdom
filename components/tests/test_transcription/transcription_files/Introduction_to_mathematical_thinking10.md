{
    "title": "Beginning of Real Analysis",
    "keywords": ["Theorem: Rational line is not complete", "Proof by contradiction", "Introducing real analysis", "Pointillist method", "constructive-destructive movement"],
    "summary": "The proof by contradiction for the incompleteness of the rational line involves assuming there is a rational upper bound  x  for the set  A = \{r \in \mathbb{Q} \mid r \geq 0 \text{ or } r^2 \leq 2\} . By constructing a smaller rational number  y  within  A  that is greater than  x , it shows that  x  cannot be an upper bound, thus proving that no such upper bound exists and that the rational line is not complete.",
    "content": "# Beginning of Real Analysis

**Thm:** Rational line is not complete.

Proof by contradiction: Let $A = \{r \in Q | r \ge 0 \text{ or } r^2 \le 2\}$

Let $x \in Q$ be any upper bound of $A$ and show there's a smaller one

$x = \frac{p}{q}$, $p, q \in N$


If $x^2 < 2$ then $2q^2>p^2$ 

 def $\frac{n^2}{2n+1} \to $ increases w/o bound, so

$\exists n \in N, \frac{n^2}{2n+1} > \frac{p^2}{2q^2 - p^2} = 2n^2q^2 > (n+1)^2$

(Construct for this purpose) Hence $\to (\frac{n+1}{n})^2 \frac{p^2}{q^2} < 2$

Let $y = (\frac{n+1}{n}) \frac{p}{q}$ so $y \in Q$ and $y^2 < 2$ so $y \in A$

But $y > x$ $\to$ a factor $\frac{n+1}{n}$ greater

$\implies$ Contradiction... $y > x$ and $y \in A$ contradicts
$x$ is an upper bound of $A$.

So, that shows $x^2 < 2$ can't be an upper bound of $A$.

But we can use the same chain of reasoning where we let $y = (\frac{n+1}{n}) \frac{p}{q}$ contradicts 
that $x = \frac{p}{q}$ where $x^2 \ge 2$ is the $sup(A)$."
},


# Beginning of Real Analysis

**Thm:** Rational line is not complete.

Proof by contradiction: Let $A = \{r \in Q | r \ge 0 \text{ or } r^2 \le 2\}$

Let $x \in Q$ be any upper bound of $A$ and show there's a smaller one

$x = \frac{p}{q}$, $p, q \in N$


If $x^2 < 2$ then $2q^2>p^2$ 

 def $\frac{n^2}{2n+1} \to $ increases w/o bound, so

$\exists n \in N, \frac{n^2}{2n+1} > \frac{p^2}{2q^2 - p^2} = 2n^2q^2 > (n+1)^2$

(Construct for this purpose) Hence $\to (\frac{n+1}{n})^2 \frac{p^2}{q^2} < 2$

Let $y = (\frac{n+1}{n}) \frac{p}{q}$ so $y \in Q$ and $y^2 < 2$ so $y \in A$

But $y > x$ $\to$ a factor $\frac{n+1}{n}$ greater

$\implies$ Contradiction... $y > x$ and $y \in A$ contradicts
$x$ is an upper bound of $A$.

So, that shows $x^2 < 2$ can't be an upper bound of $A$.

But we can use the same chain of reasoning where we let $y = (\frac{n+1}{n}) \frac{p}{q}$ contradicts 
that $x = \frac{p}{q}$ where $x^2 \ge 2$ is the $sup(A)$.