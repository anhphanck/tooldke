
import re

delta_t_text = 'm\r\n\r\n=r\r\n\r\nnay\r\n\r\nAt: 21.792 s\r\n\r\n1W/At: 45.89 mHz\r\n\r\nt\r\n\r\n1.737 s\r\n\r\nAa: 126.709 A Aa/At: 5.81 pAVs\r\n\r\na: 14.199 |'
t_match = re.search(r'\bt[^\d]*([\d.,]+)\s*s', delta_t_text, re.IGNORECASE)
print(f"t_match found? {t_match is not None}")
if t_match:
    print(f"Match groups: {t_match.groups()}")
    print(f"Match span: {t_match.span()}")
    print(f"Match text: {delta_t_text[t_match.span()[0]:t_match.span()[1]]}")
