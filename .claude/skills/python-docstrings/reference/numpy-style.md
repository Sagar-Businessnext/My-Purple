# NumPy-Style Docstrings Reference

## When to Use NumPy Style

Use NumPy-style docstrings for:
- Data processing modules (pandas, numpy operations)
- Statistical or mathematical functions with many parameters
- Functions where parameter tables are clearer than indented lists
- Modules shared with data-science teams familiar with NumPy conventions

Use Google-style for all other BusinessNext Python services. Do not mix styles within a package.

## Function Docstring

```python
def calculate_discount(
    base_price: float,
    tier: str,
    quantity: int,
    promo_code: str | None = None,
) -> float:
    """Calculate the discounted price for an order line item.

    Applies tier-based and quantity-based discounts. If a valid promo
    code is provided, an additional percentage discount is applied after
    the base discounts.

    Parameters
    ----------
    base_price : float
        The undiscounted unit price in the account's base currency.
        Must be >= 0.
    tier : str
        The customer's pricing tier. One of ``"standard"``, ``"premium"``,
        or ``"enterprise"``.
    quantity : int
        Number of units ordered. Quantity discounts apply at >= 10 units.
    promo_code : str or None, optional
        A promotional code that provides an additional discount.
        ``None`` means no promo code is applied. Default is ``None``.

    Returns
    -------
    float
        The total price after all discounts are applied. Always >= 0.

    Raises
    ------
    ValueError
        If ``base_price`` is negative or ``tier`` is not a recognized value.
    PromoCodeExpiredError
        If ``promo_code`` is provided but has expired or been redeemed.

    Examples
    --------
    Standard tier, small quantity, no promo:

    >>> calculate_discount(100.0, "standard", 5)
    100.0

    Premium tier with quantity discount:

    >>> calculate_discount(100.0, "premium", 15)
    76.5

    Notes
    -----
    Tier discounts:
    - ``"standard"``: 0%
    - ``"premium"``: 10%
    - ``"enterprise"``: 20%

    Quantity discount applied after tier discount:
    - 10–49 units: 5%
    - 50+ units: 10%
    """
```

## Class Docstring

```python
class DataPipeline:
    """Orchestrates multi-step data transformation pipelines.

    Each step is a callable that receives a DataFrame and returns a
    transformed DataFrame. Steps are executed in registration order.

    Parameters
    ----------
    name : str
        Identifier for this pipeline instance, used in logging.
    fail_fast : bool, optional
        If ``True``, stop on the first step that raises an exception.
        If ``False``, log errors and continue. Default is ``True``.

    Attributes
    ----------
    name : str
        The pipeline's identifier.
    steps : list of callable
        Registered transformation steps in execution order.

    Examples
    --------
    >>> pipeline = DataPipeline("normalize")
    >>> pipeline.add_step(drop_nulls)
    >>> pipeline.add_step(normalize_columns)
    >>> result = pipeline.run(df)
    """
```

## Section Headers (NumPy uses underlined headers)

| Section | Underline Char | Required When |
|---------|----------------|--------------|
| `Parameters` | `-` | Any parameters |
| `Returns` | `-` | Non-None return |
| `Yields` | `-` | Generator |
| `Raises` | `-` | Any exception raised |
| `Attributes` | `-` | Class docstrings |
| `Examples` | `-` | Public non-trivial API |
| `Notes` | `-` | Supplementary explanation |
| `References` | `-` | Algorithm citations |
| `See Also` | `-` | Related functions |

## Parameter Entry Format

```
parameter_name : type
    Description starting on next line, indented 4 spaces.
    Continues here if needed. Defaults and optionality noted inline.
```

Versus Google style:
```
Args:
    parameter_name: Description. Defaults noted in the text.
```

The key difference: NumPy puts the type on the same line as the name; Google relies entirely on the type annotation and omits the type from the docstring.

## Configuring Sphinx for NumPy Style

```python
# docs/conf.py
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # parses both Google and NumPy styles
]

napoleon_google_docstring = False   # disable if using NumPy only
napoleon_numpy_docstring = True
napoleon_use_param = True
napoleon_use_rtype = True
```
