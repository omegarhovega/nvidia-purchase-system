import random
# KEY CONFIG VARIABLES

# Store URL for desired graphics card
NVIDIA_URL = "https://marketplace.nvidia.com/de-de/consumer/graphics-cards/?locale=de-de&page=1&limit=12&gpu=RTX%205090&manufacturer=NVIDIA&manufacturer_filter=NVIDIA~1"

# Old Proshop URLs for 5070 to be able to get the cf_clearance cookie
PROSHOP_URLS_5070 = [
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=e9xWqlpuKTjpX4mjkI24ALG44BCzDC2pB7nmEMmfYop%2BOXdRl5K%2F76S5GqpJ60DK22sy6puJe71jsffBYtaYayqJ3XtRtj6QRdF7Ko%2Ba0ToTbJsJzb4sbLyTXi1xjjwgkcc1KUk%2FNivBVRs6JjfGaCtA7OrzknUkwvcVj%2FksXi20NzjlKzOxR3HTI3AjBgaw3ZHwRPWbOzgLoe8J1J8ImSonrG0SYCeH2qOSJg1b37hRAEQUVIpQFBKa%2FWj8J5RHG%2FyMJqRzXC0WHMmPN0dN0H5rDj8IxJ0j6tojkj8rbgPU%2F5rcn5huJILkgAb19M4Q7LZGtmW%2BtUY2phgQrpGWwA%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=WBqR2lau1Cu2y3PDsRJb%2BSr%2B7DZEtDykpuT3lIjekGtPwdcQl9B6C2bb9UknhGL2CI9Ic0CpsvSgA8zOL%2BRT%2BtZo9y85ayDNwOHtrfHST%2Fd0g629S4FzJqfV28%2F%2B%2FFzidbYK560Ego9FhD70DkS9YE%2BgiNhjkk6p1mr%2BFTd3pp5hvcNwJFcgtMADgOclfdtJNNO2prdwW%2FbD5yTwxrzjPOSEzSWp6673Xg4iQBg0iBFjPyaI1cepzbNQBRjVG7uh7r9qtD%2FGu1VBKpqOU7LtJvzoGadc0ahrKA8WQ76QMfHiE911BtlK29PIt%2F9R1QRdxHUZ65z8eNIzSZFGZm9kyQ%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=eWRnfPi5xDbK8YZ8YR%2F33xv7kDK%2Bnj5Bbq3o8uXgxnouIt0iF2vfykLwrcWA4T5KNof%2Fmu2%2BlyeD9LPOnWu9Ekna398EiCgF7MjGUfFSOgscrmq5qB5EjDvS0%2Ft%2B0%2BtuOg%2B70wiKB7aWlAfDKT8DzKgFOPRJyg5mYiwg7eXtYQuXiuOT5LO9Ch2o6TQpNpwuu%2Fr7dV1dQGy2zrNtDufSccR6zLcvDi02KffxQLQzAwpItEHierzTYjIhpwCYwuK9jB%2BGlcpHVWgaZ2gqpPI3yzbyb8%2FOizTDilIQvIX1SeD95eeUY3FMfTo%2FNbJxfYXgBzn3l98EshsfHQmhQUKyMw%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=ViqXsFWl1FrkvJB5MOP%2BHg6pnV%2Bfoio4nbj0G88Jqz7RHVUvG%2BGQxn52Yo0eIWr6rD3cvHMKCkToQfygoHB6KVacKbE22UsgLz4ccVWar8OSQkDPsL0X5pyLL8uojuxTa2hRtD1krnOJJZF17qEPAtfzVFIrNnLnfYspVpy4ZpBlw3gr11P0HNxr8eE9tHzqWHD%2FA1HBfAKgHfP4k2EWCMbx14v55zZ5phVCu%2FJewCsqJPUvbw3%2ByBlyw7pPZbyf3X5l9RSKi0U9H8TfIzgVTXlf2LDXCI9EY3VepBstBt%2FPUkYZgwFwQDGSxBBdz08bSmeX6ZlP2M%2BKh6WFGnUy%2Fw%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=WAL0oJPWx51kmEowqN62xI7HAvdCv7Ek4wq6qPLp7y4w5HAXn8GubecHpfYPqeY1KUJvIzxZ1Ve%2Bs%2BjQbQBVt2oymkN3AyDOdRAu97fXPFYmn3g9d7L0nOsucORJOMhTgBKNOhyIqg8ShkvvxEpdBg9AIKusn%2BGPyynwGd5UdcV9p8P6rkDTv6AXnXnelsYnhgtdUJXnxlKqCICYAWj%2Fzx3Klko61hifcfrkPC%2Bdrt4904Ui0gUKV0vIgCEVe3BlYdP1IHZmuFzetqCtPYe0EhIFGTqKpbsWK%2F0uVxWLsoF3LwK7gbYuAqYHCVga311G7XcYy%2BOOLgkjEHEPetXlbg%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=PQl728HdZJHnl4O6Aba4Nyc%2B2MujJ3igNvQA9KwBxr7ea4KBKbjZqU4bu6B7uePq%2BZ%2B9IOc0S4NvWJ4eEa7YJteiwF4VFCirJqZdXteWnA9wfk4zNHEuL6KIxnOxcr5Uv69oxr4P74X%2Bo6a%2F7amuei7r7JLhTGus3%2Bg83qURPniCZ8a5fSScsA1phy7GvXVDP1X2M0OUQRU%2Fr5GdyZLlvxVeKmgv2uUNxUUMM0Z45ZN1hXLHl74hfatqUnpsZkfTh13j2GbwGhtr0j0Dnsz5jLcowxcUJQU4X5pQlku%2Ft9tr8rCR1kiBNE817E14TZ8PvAibQAUAxYREI4QawYjD2w%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=GUURMuxhKoSWfvAXn4OwUofTvBNYFSYQVDs6K6qMNUb4MEuAFllWEA28qF8rO%2BzvJsLsq4aBLX1DTcdE80jhrrUxO36kP7U%2Fsf0vCk3GrhrOUFN0FHieWpCcQf43zPOTd8OtSf9hlZkISyb%2F%2BY5Mkr0Msg%2FH3SmpW5I0pZnE1rsp%2BWsnLy6hEeGs%2B%2F%2FUZH5dM91Ckntx%2FPn%2BE%2F1EMCHefJKGXniB7vvD9a3MqQPR5lGzujUOdUwl1jaoDFsa5Xz2rCHkWWcjNBifkQ1uLSDPVtSmzFDy4ydrRFtt3xDhpCOAng0u4QpXX%2B7ca2UinnmnIFoBsAejEx5UwC3bUU%2FRxQ%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=JWIxYWKu%2FfAcP%2B8tigrUkv0v9hhlYjrALy5k7kiS102ciZD%2BwjuxKAlk7scqi4lzlO0oLWydcQThWJOqOla%2B4d94iWD9emQKlF94YyYKgqBAFqLH%2Be9DQCWK4Z%2Fhack9COaWelNoZ%2BRbRiupoYREspB1gx9oIJX6hXmXS%2B9sHuCckoudztTOgRaOT9RDVcDNcCXXsOtfQhmaHryBhkLemaWKNbD7u17t7%2FoISefwLMbDXaN96G8f2h0nsq3DaKQyLGilfBBV4PmGsjU0qDi2ThxgPLlY5%2FE52Lr%2FJNPPbZvQpB6K5WFVtv7K5jTGkdywyS60rQH5sKZSUAUjhxv4Lg%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=VAeNbaW0FnlxYaAfXIGeXWTVUaVKklIgRRqa3PzXnwNa5kcTEYWI5mVYM9C4jSLEs%2Fzd6%2BIwqAcVIBWJjW%2Fz8D%2Byvz5CJUsyEHyBn64C1sVPErlXVa8VB2Wy5WKLduFLlB1pS5dkOxRwmgwtIfEdfbLRfSUJFIN1oMyhehiMb4jxarJWdOXAnEBegjguvUktQ6z2TbvF3GTuILMf0ACPgB3Hdu0ej5tY35554V7bN8kTLGIbKzt46tvzjeCt8j0I8wXUmow3z9x44JegvJapZg%2FOIA0Cu6RH4qoJmiU%2BnL0bRpLemFVtZZTY0LrkUGOO4eiYQQL1544d8D5IbpgBig%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=Lc%2BpBps39EH4khY3%2B%2BbNZQ7leBwZ393PHc7SMkyU9CLUaiT0b8jKrFd7TU%2FNUhxHrp3vOnyCcrxO190mzdO%2FoBaD2cPZEBXB74WowGDYMl05QuBtGtCcm1k7L9dHFfFtj0peZIchsnJ7RTSAD1o69%2BxCyjLxu4%2Fdn6aX2Otb3Wkdh4KPuK2cS%2BE3yLL9zeItjxTwJpbUg%2BzJJRiGKLo8W77q3oLinzmecb1KhKHsWGP5LI7GTftirFSII%2Bgcb%2F3YaGPe3XKbFvNzgYzaSQhl3mPatj8SPzwODRAH4%2BNGpIBSpJUdPwbGWMsMOYDnSkHhoJjAs7FgKdpdCWcBhPJdCA%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=J5Lrbm4t4d8jII8PEqFZfyhw6V0wxFqYUyD1HcVfJWrX3SAumb3O%2BEc1dz34sPjP0q56XWNRklWOwss8A4S9yLcH%2F5HJGUiQchnqE6j8msGprvmt8TvPHzMjTnDb%2BC5MV%2BZypRyIaJbRj9E4dRmfK5Sk8wPbECijFVD3ZivXVioKQfRZKWQI%2ByQMUtwIx5M1Z6pj0Ic48YHNmYD8Moi4blzA7Ptb8NIfTtuk7%2FmMjRVUO071QmOITWOn7pKEzYHXtY8oLVqe8Dd%2FcnUsPCggAUIBkKjKXdW7eAc4lgJb6Fxt%2FenK%2FqG1nR8gWzQaN5q6mg8Gaac9wsiQV8NIh3amog%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=Dak19rF6dzQYXpQ5atG86oegy7Uxn664Ve2RGirv37C99jP8czYu0%2FyLlWKIBTTT01euckiQf%2BQFclvnkDC2%2FT81zvYTMW92KTfto7%2FtJdd%2Ft0VKZg1YmIr5ZoZYBHGq1he7gvJdhYeBfTKyZnT9aDJVcrxqgxps6gVYobv1UX1Q9HnixkKc9tmLDzA2ww1lgrWRRwLPwGLtEsciHD76JQSi4J9C8O19GrkUGqGaOjZAO99SqeSjkfztfgqoR0EtFrJ33DeeBX3C8awAgnryby9OfVldpjKUhp2hLkK%2B5FH1c17A6%2BKCiu6oKzRFLLIhkP36roieatVvKL%2FaTi827g%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=QfttBK8RmxAxt2RgMdohov%2Fp1ZKv4kEuFu6gJ%2BpeYg%2B3CESvd7Fuqx5XTH7FT76l9x7ZNGuth7S5W9msgTXePy%2F%2BDN9VvwKHbl4aD8IxV7NUqCy2Kc4eDeqnwNRChcJy%2BV%2BMWPCZNzh8xoaf9M14uGmLV%2B7fVNTEJU5Ru9hRfQuPOuNoSqOCPGIyeTzok19GiqtMILceROaF1UQLtSZRJZP%2BqJznJBGzzUc8hePmCvENRA7GY%2BnbxDEUbRs4Cz3l%2F8Mx31%2F3aFEaAbn7Q4z6hEKdtP9fLy00RPmn%2BtnozJAj9b4GuG8rd9qGsDkMyilDVTBajXpS%2FHwk3Ane%2B98Ryg%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=ZS19BoOPGQ2GICdQsgXIrRnhwfBPW0d1RiQW%2FCJglfPdIB8H%2FGBjhJQ7xpRo2u5TH7xFW4A3jC8PLR%2BDJts%2FZk%2FQxsz2w1AG%2F4tnDUw2KbpDAWSDDYuVqgvepLyQN6sgyTGgiv15EoftNo9pS9Gu5fORuQSmPiNpHUfh1vVx8r36ovkzT%2FNLzgq000eozaZQBCq7UvcqqOecJGZoUORt7AEEvvwR%2F%2B6sbY0ca9%2FhVNFoQLUoCiuGyEQDYhmAtyMLl0J5d4dM97zmJ%2FDdhSoUfxNZvohnpbjcOUk5dNptK%2BuZM2B3y0JorBVgPgY8s5TvhSqeBCKZG1MwORtflnwo7w%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=XFUyFen6h%2FTKxd%2B%2FssZMQ3BytGO6MZ9TfkiejBvzc0t0gXuan81yZrudU4ZPp%2BDHn9rLKMkuBGjVUfHY7IDvJ%2FRfHWpiGFZjZnkCS5uTjelTit9nlcQH6eNwBKXoR4%2FGis58p8%2BJLpaLYQez9oI7g%2BmbVxRYbrk2FGfInkKFKjhiAcrL8WberPUjfxpAz0dJOfvPdcU%2BQEMkvW%2B1GL77sXNzXFdrerLvd0BFadK9bUn4FUe42yWegSzw6ZYRf9yQ%2BI04y5Y3aACosGSRn3vKdb3BFFgauZsvh3lc%2FpZiZiyp4%2BeRGw84CBCX5358xThawozf0gQMYa6NjpHMSe7oJg%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=YfU80OIAuvyiOQXZojzSaFKqj470wQxGlG2pcvbWsBnZGZxRi9rJ6QAj0PU2OUCT4qVBx9YtL7D2NLl8va1%2B5A5jMbfa0cD1pkUVa8PuL3s09n%2FTseHge7ZGdiKLxV3qR1s9YcFaXzc0ANYt7%2Bz2nMDA%2FQW%2FMCwv%2FCJz3KA9VN2AzSiG3%2FCQTxojEBD3Kjd0EXo2O2nqrdRV2Pd%2FbjtSln93M%2FO3esvW1%2Fk7%2FC3uFPVY7FOYbIKWey66FjM3euhHJe%2BhM3SFf%2Fe6il4cdzV7BPvw61fC52MsXplJMECDSHvhJsTxdC7ajCeM9FMMG8u%2Fmwvvil7W0qixn5oNwC1Uxw%3D%3D",
]


# Old Proshop URLs for 5080 to be able to get the cf_clearance cookie
PROSHOP_URLS_5080 = [
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=Y3ccbxb2pHuq5dElEugtOQnlQ4S8UfSLpqrEQE1QkHxoYkLCPVyNhqGcCh3P2B46A%2BT6sQGnIRmgoJ1zpflg0hqwGiS86X8rw%2BlnDai0YpqifOipCfIuT6po27HA0WYaflq1jlmDB0Puye6J%2FNc3ljDr%2Bcq49wSh7tqQc9xiH50ijxrNyMk1zg3U35VqfgJuztP2cLCofTFoa%2BjCA1GdPh3cSmct8x9%2Foj54eEWJ0Pk8A2AhD4Y0ne7CrITnzOLW0k%2BDTP4KyPbEgmC8v5%2FVkVshnUZlhPdSoP9EtDwZ3yD8TtNQrFarxCEdMLsnXNlRUReocTIDRIWuhLxMGATByQ%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=ZGmF2Itbx52FQ%2B%2Bzkd4SfK63wUZF%2FsA76ZObHzHkqQVXsGtAI0Z2tPljSghaq6n1vURBpnGt9WRIh5g07lWVQrYktGgIHAElB87lZKtmCEH2C4qwfGYk5Mvl5mrvM8%2BnOP8nOGsAEoOib4xl2kxZQkLxH63sIcO%2BB5Oz61aOvWNR%2FFWKVSnuWIl1g4zWSS2qdKuK6PeT86DhKtPr%2BwjRMsm1Vu1gf8OBRXMDnl3HrjWf7PqjcSLYTSRFQRcuibiZBjdqsLqAjFywgESLf2Yh8RcmmBzawn0cBKVeGyrWWFB9Kj0DNwHA8o2x%2FaXniXi4U2qBI%2BWNTqIlcYsYbjP%2B1Q%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=GBKIrKhIKjGZiaEp3dM6dCpB21gNLQqz7sGmP0pbk%2FPoWi49Sy%2FPIbGXcN7Kzk8IL2USzpH0fatKBtyBysEuByYRxanrnL8Bw5j8Z7wN%2FLtWQm7dkmzT0ZL9ufG1M6WlBb1dtrxQ2%2FRsuYsF6KQa9EBFWlgHw8eFGPxaTO4%2FGczsQAcrcs%2BpppRW2U%2FlVLhL1Eup3nas2CLSF%2BNqdUNT7z5mbA%2BgDWOuIJWracJ1UBRGF1saGFss%2FLg1mHHpHP09B6IPDvZG88QbO1VAbMTIvHEqDML2JMgSlSXrYu%2BhF2doEGAqs5I7bOloiYtY6HcVM6bC9xiDa6g4NYf7ZYg1iA%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=JHcPbieAdEyH2g3%2Fi3hCynNQnPJw385ovCCdcA1UtOIippDFBYXJ1jQB%2BDZsVN0pwASL1elD9EVT%2BMnrYCpHyx99uJL%2FywXg9nmfbOst4Qw1kUJqyE7UgCWFQSps%2Bj9xUHdtRGbxHV2615QGokVGgcz7DV484rhi7tP3fwOta7sDtDGqSIrr1cKIZ%2FvI6JnpqUvBJ6MHNYIKAe%2BhrjZi8ujnkcJDBGFM0L9%2FeoRrOMX4Ngb5ElX5FSBH7e7iKyaoqH6W8z0dzrGsbE0z94v6k%2FBBnCJqu9Y6oMgoVDsikcJcYpIFGwuF27%2F3pT0kWmWJ%2FXvBCOhWz9jM5PP%2FNgHUug%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=fYqeInMHAHiN2UI6S7pfqh7YS1mQqFKsmOUTpCJG9CcFzykJT%2F0m1JiXEdw1clBsiQfMaZIxEPcJ7%2BqCmPZ0BtuvGih6K%2BNFw4AgYyKV03N4XGASOI89dAQa2lAN%2FX%2Fxub7SntkGwmd0vdnHWaCefl4mAQ%2BJUleJmFdP8AvZJMo%2BuRaPtJolkyqTB62zZFnsAnkTJ9TSdJJLP9sxhCBI9eTF7qx4ktDaT042wtAMW0cCGVbok%2Bct5%2BQW1kiRL880FyJ00iceDOR%2ByFynJeL0ntEESG9%2B3cxMsTg6xKuordyIGMpKIqz2URGVO9LBJhFixWBUBFTda%2Bn%2FpjTJZjnTbg%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=DT6e%2BjMthjSm2pO%2BTt05BLZafxpwCYY43DYvuFHeo3vPAiXxaxA2TWJxW%2BFaG4GjHxySNYXqcxCwYpD46wJZDRmk6AZFTIyDbVB96TwuAhFltT%2BGHWUXTOzN9rVmMyP6dDit2DSCDUkNraJF3azRQ0qFov9mVsXvNWStUwTRFTcCh9bjS8BJgqOpeSkdPiMtkFLoE3XCXu4EiLow8cRGLlB1%2FkGou3yMjaTwg8gYjVO3J9zJN9BE1vTZih3MtzHE9UlsTbmgFNytZPgr4guQDqsazP%2FxSyRrd1LI5pyxm1YB%2FjTxfkZ3WKUSFdyn0XOZ3E8tl9dZbMukIOh0WsU9DA%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=efuWIgvOkGDYvbAca8H0ws9P7%2Bw7ktw1TmSskfbVbSsUB8cHottl%2Fg4PO1MCH6o8QxJk129XT4Ankfq9lliztoid26IM6GlQJC15Cxz1pTCpovt2Ydbn1vkj6ljhyNMCIC%2Bc%2F4UbdGZch3dN4qlcJ5soHakO1bxebgskdMMr5cGsNBxmyCcptAvMbPeObs1dO7NuCgg3BLRPJCo0L3ilYOWUxE%2Br8D1GXhcXqkWlIDC5ilh4l9cB9%2FyKnNE3Ja9w2UxTCLiB9mFoerxqGGpDGQxh%2Fsihk317hN1VZ3YyUUCc2doNJSSQy6FKAX%2F%2Fg%2Bh2EAfZX4vBDY4mJRHRb7q4Pw%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=BbFbP%2FNcnQhekG5rj8gNYkhHFOqocsAeTZFhjodSbXpwJEHz3I%2Foep8o3Zo8y%2BErKEJNNdxP1n%2BgFog2DmS5TSs6J2x7Z1Sq%2FfWpms3wjjyw4quxTDZNbI6AOf2DJbM%2BdIrXhc7EDCyHHGnubNV779iQjTK5I6x%2BmEXMJ095kIuRepEV0Hxn6VleKLt5aCYB3C7ikpjUkrfpQMX78xoPkMPJfIiSf4KY%2F%2Fz3C8D50hA6StQJ75X%2FiNbZKx1DoXTXK8PUpW0mRYelH%2FklWXa6LgqdCozd%2BfD4naESxatti3TyzTYqqLl4w0kTbq0lrGd3Z5JZKXUXKZKEtcOOZEocgw%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=F72X1evgI%2FegSVY9%2FRhs2UUiNZtjJE1GFPQJLnndx58Us2oipNkFF9CD5RsSmW0OcE%2BkjS2WO9RMW8udNqezGTH2M6VWWJtykp8AKJSuK9kmWudlI4a9hVhA6NGgmf7ZG4Z2d9GBJ2dSDVISzEKgmnv4Qigq2tXhSo64zhVhiinh26Ouz3HlseSvmgwVUtRhVHfZQuoBwNhOmxhaNMFea%2Fw1si60eIDAzBg4XSvI0Mpqostkm7eN1QWEjkm6%2ByC8hEkxJoCVETPUHHuggzRD6HOpVJE2TnMlOyg6EaR8kV8O1Q4Nc6SPg5eatBrwA4X2TsFXC8T%2FTxqZZMWycEqgrg%3D%3D",
]

# Old Proshop URLs for 5090 to be able to get the cf_clearance cookie
PROSHOP_URLS_5090 = [
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=Uhgm3Iw%2BgdsjYpUtYecLzX07kCdjGEsfaO9TU26jBH8%2FIdzmXcaRrDSo103ljFbD7lgnLyoM%2ByeNVx%2FhVdMk%2F9hHLVV1rEsmSoo6sSSmlucg9mBhuU03%2FAs53nMAvO5FMMOE5sTU0p10d8z4nkQKOVLJD13VRJNWaoGpHrSi%2FllpHNuKQQlhnb61EYMT%2FSfAlYLcebLzBRP37SS3QmBFFlxolRtN6AwRE23VPjzVDQED9PeBXKlMNcd4qPAfLPSEWVH5WKnhz27OL5C9nRhA1yBJ1mi7Tthdx51VO6%2BM%2FCJ7kCDlIW%2FgvB0LhXoPPOMU0Eq0d65MmPA%2BHeMvXBaa3w%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=DBoN9dv1xUnC0AnAKo1xrvjvWpeQGMDI6itlTZ5Ko%2FdfGthuD%2BHhmfAkZ3dtiJ5zyz9tZyJ9KTcA3W1OdtitVx9p9oAzZaha7Rhzat056UeVQFr2To1NBVguaA6IbkAgtGIzJCnN3jjc8yeKUIThmkNPc8%2BrzMmXLlSmqow108iYL25qbsYhMcr5PnAeBGputnpBN0dpSii9RcpERcNlGExGgEUE%2FrHSgtehG5Ynaf4C0Bftw%2Fglwxar4YZh59UUao3ufJic3iOyv8T7pqptDRsp9vM6TvslnQI7anAFP2w5Ut2GUrciYLg3xTNY5q7QKgMEjg41zAb1g9NkQgXDWQ%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=NIuab8VFf%2F8x%2BA9d%2F4h68kZunl%2B39oaRC%2B%2BB7pINZIS5XQ8WSy4TTVGUR7ZEcQFkADZPmqfxBJzpgjksr3rwDV3C2KrikEp%2BdreduKrfVpsJJgkJv9Mjy9bqMMumx1Laj0DkbhDNj2UdTNtuNhol7aHBawa915iScBEPVCXIaVALjTiyuCLyZeoYl5nSOwIc%2BYJZ0%2Ffr76bdbdtRUGV2azjnKXdSvZ9mpy002y8Y8eCI%2FJLgIpvixK2UmUa%2BjvSP%2BGKe%2BotbuJi1r%2FWuVZoPr%2FaiOWKyTmXadyuLFd%2B16Q44smMwiLuo4XTLTwHtyhtFSs0%2F9H6MiN58m8DjQPDDag%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=cGGPxfRYyEAQIZcnhxjJN%2FOLLxYo1AzRUQ5%2BCEZexiwFBOSjMwsnanN%2FXJ0oRu2reyKKP2C6CluQlS02NEzu%2F2ZEeqaN2Y3HjoPNaEwG%2BF1fDICdp7GktQpKQe1vxC%2BeMgNZxQF7g1wN3gsXDtXX1pBZH03W%2FC4UHDdyQJGLWD4sjITj4YS2QZfcjYV6oqk5Um4FIB7CBPgPwS4XndSYxrTwF8SPJ%2FnJoknsHS2Pt3mJTgsq171Yz8blP04AmETPm3g7HSDUwyuu7zqFmAG61iIzFkBoy%2BvIq1MrqUPcpBUZlFNbPD%2BtCsVuhLQc6kwQOlzYWoiBUQ%2FJUetzApYEMw%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=e97%2BsIN%2Fy5TCBgbJggoLh0Bd968YoxY1Mqn6DYAjZVJRJfpLDYIAvaSjYIjnBc%2FOb3tgl4wZ9h4p05ZPBU%2Fwl3ICDequhyRCQsr5ZuLdTDPrIXQV8ppcJqKErdKBVUPtbDEqlwALOU%2B3djJlQ%2BpRtbqkH%2FqE8%2By6JHstHay2uxyXNKW1ZufsXGmLKgWMv2U%2Bu%2BJqWJ1GFrW07ILRhmjfVEbjrWEBKkyMDJr%2B8cFPu6PodeId%2FHJ6OBeYFmud2G29YExXMIVkP5oUWR3YOuaAawsBu4bT%2FFIWGmqBM5%2FxkEXmJkznEp7WejcPHD5nOmRlS051CXKlEPiUsd%2FAMatoyQ%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=C8HgkfqkAbdVIyPnb%2B%2BHQOoYO6UhnuDDA8853HMVzu6Wh3v2YAtSuPC5hOcGnQqGZve77PQt9%2FdBgsLw327GJu35bgsktZFF01sZq2Ggu5VIedzHT6GMr%2BVdEl%2BqK6TJO6kIOoOFHkGPYbDnU8scv53inA8cgPvwQ4n8soRyD7EDfEYavWDPah8%2B%2BIPQye8LL8ymAba361B0pjcQgb1L2a4ap8SgOYum1voEi19FqaiPbcOn%2F1tmFZfTqw38ZrsV0wrokDAOcjaGLeiD5ujyc%2F9uY7GAJRGtEasilCzFJhECHYSimA9q8Pd9vJh%2FVhd9j%2BW3WlTmmTM4Pt3vimM2KQ%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=KKhHB%2BRgii8x9Whv7x6dUL2nbrrv74sLzqeEBwmYZdu03QDimI2NX4xjLmz9%2FU5L2gJesyGEfh8aeX3xmtrfgYzP5a5aQ9a3wuJLMcY0B9lUOkV6qYfjMYl2PKlF%2BgZJK3xp9hwW5JtISujKif7wilHdCCnfTltJ618tLL6Wa7g8XyjGCadvG2VSieua5s4ZLL59n9HNsSK%2FLPGWmv0lAd4LQw6yFLhEGqZV6JQalg9IBj8NORidB9cjPXkq9iHgQYqkID3vdDRhJ50tgy4LQb7%2Frh93x6wvOOhEUGLnMXgkEFMCUowdf3P4WYof1280JemQBZ%2FYuSexVfdCFgwplw%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=S7zVHpMFRiSz60DY%2Bi%2FOr1t%2FFiY%2FW%2BA9JU6B0TkLNcftxhk%2F6ytUmxiXzwaiIyl8WbM4gCYvT3McHBk%2Br0i9yxFbztVWnSd%2Bai2dX8nnegGH4qagekFj0wZ%2FGY3dk6KhNkiAIdKwKdDNq6OIqeNlEzTvbdV5XvispuvwTOMqXbuaBMzeZyxEighyqaKeS98Ipp0K4gpG3HyhZ1wgVRjg0W1MxqGcn9w9h48U7AlFVOB1rRT7VgmAngbGxNOwKlTP1q%2BHegA7cShH4f58ZbmCv2r6YkCsC%2F4JoH4bL4aCZzMG1%2BgNY1c5Idl4ghRhKJKCD2IAohR8ECR1BmJDd5WLjw%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=HxFI3PyYFsv1XYdAV%2BcuykCMwIfy2vdWLx3x9aac4f1eiglmBQtvSDIbyXjXY2W%2F3nDHVcPrP%2FNF5TpuNb1HJtLyZzE4PJwHIlwRNTbf4njJiSMTOQdLp0Znz6vIRIjdhsnudmiZwWZVV0VnH8slYbUmaXoGahR5IoqlPDgNgmHajPtCcu0hd6iL5vcRYee8%2FU9JvW8KlGQM3MgLuiYJjH2mLlLkVDDrvTxV9bCygQSjiUJlA2%2FVApZKUG1I5DN9vtuWrDUuwduRGJk17lo9w5pbJzcl%2FGuTRnw%2Fm65Un23HzmzoDNpqPE1h5o4bnL5BKf41aIfRXZhlQnC2aqwBmA%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=S05eW03TIiy6uwMj3tTlEGoAdZba2gn%2BzHG8oBCMtRTspRCKoQsIe%2FdYbizV7Xft02G8ATZe%2FVQI3STgmq0SvZEe%2BbFtv9EEaT3o%2FKe7c3Xv8yK7is7sh2h%2F9UNnjSzKBjEOdITnB9JbOLfGi617mZh%2BAG8c6%2FAvnmvtSMXkIhVWwL4q3Jm0SnTrRLawZhGj2RWxezKcsLK1rdPSd%2BaofjJ1EoKwVu7ZU2aOn%2B3LwEBJIJUKjasW4yVHrYEhLyu63%2BD6OjY2EaFahGWx%2FQKo0hfTmElGC0g5onbKaGSMENspjNLpA0AdWts0WPdoKYc%2BbmgpFqy%2FdYT7n0SK2zWOQg%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=YZ9CpitOe7diRdixe0icm7cUiignFAyZRQQ2qUh%2BmgjbohJuTOrsMtiK%2Fbwqb9JFCrEZxHK2CcqmxILcI7caCTBf%2BucEjg1x9TPi%2FXxklSy0MzLJIXKrX%2F5Q5Au9YUS%2BqJpGydelSAt77iplIOKorc5SW5nJ2%2BD%2F75IW5Hho6ql1ZfCwdUO%2FiWMbz7rm4AzX0ObdfnQMsGYx47d2RpBzZuWQ%2FrvS1NfQb4aHzq8GCWLC0A6KaXFpr6RaDlMHULnx3XFKQWBuLSPb2q4qdh0udcKXx7BNR77qZ1a7aqf4pwgASKKcF6bvw1RS9weF1jY8C5rnfmD92TrNG7lZNYKJzQ%3D%3D",
    "https://www.proshop.de/Basket/BuyNvidiaGraphicCard?t=bFHncOsrkXFbYRF56H68bUYIDb5AcZcdMLlBR44dZW46fqwfc5XdgVX7GcBoTv0MPqdirRx3xR%2B%2BHzx%2BBotzaO%2F4L%2FlTqKPHplY5e9vGhWSXFRzoebTbYEhykPPVXJ4u2DB0yTMDccuO1cXeoNsy2MRNf3G9p3fUSVp9zASLJ0uJymzkdEijj0QKsZLS8I4GQ252Y7yAUFDboHiEt9TDvJ3Fo1HXw9KXeueIUZ432lQhBuzhHR78O9N%2FbJldC6r9YdeRgCszPH2m2u7VRaaZPasTuvylSd0yj7tOxQOTou85%2BV7D%2Fw3brZng%2Bc5t4CE6vL0qKGsyvL4lH%2FfCE3YWkQ%3D%3D",
]

# Stale Proshop URL to allow doing the redirect to get the cf_clearance cookie
PROSHOP_URL = random.choice(PROSHOP_URLS_5080)

# Selector for the buy button on product page
NVIDIA_BUY_BUTTON_SELECTOR = "#resultsDiv > div > div > div:nth-child(2) > div.product_detail_78.nv-priceAndCTAContainer > div > div.clearfix.pdc-87.fe-pids > a > button"

# Inject script to mock the NVIDIA API response to be able to follow the stale purchase link and get the cf_clearance cookie
NVIDIA_INJECT_SCRIPT = interceptor_js = """
        console.log('[Interceptor] Mocking NVIDIA API response');
        (function() {
            const mockData = %s;
            const originalXHROpen = XMLHttpRequest.prototype.open;
            XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
                this._url = url;
                return originalXHROpen.apply(this, arguments);
            };
            const originalXHRSend = XMLHttpRequest.prototype.send;
            XMLHttpRequest.prototype.send = function(body) {
                if (this._url && this._url.includes('api.store.nvidia.com/partner/v1/feinventory')) {
                    Object.defineProperty(this, 'response', {
                        get: function() {
                            return JSON.stringify(mockData);
                        }
                    });
                    Object.defineProperty(this, 'responseText', {
                        get: function() {
                            return JSON.stringify(mockData);
                        }
                    });
                    this.status = 200;
                    this.readyState = 4;
                    if (this.onreadystatechange) { this.onreadystatechange(); }
                    this.dispatchEvent(new Event('readystatechange'));
                    this.dispatchEvent(new Event('load'));
                    return;
                }
                return originalXHRSend.apply(this, arguments);
            };
            const originalFetch = window.fetch;
            window.fetch = function() {
                if (arguments[0] && arguments[0].includes('api.store.nvidia.com/partner/v1/feinventory')) {
                    return Promise.resolve(new Response(JSON.stringify(mockData), {
                        status: 200,
                        headers: {'Content-Type': 'application/json'}
                    }));
                }
                return originalFetch.apply(this, arguments);
            };
        })();
        """

# Inject script to solve the Cloudflare turnstile challenge using 2captcha API
PROSHOP_INJECT_SCRIPT = """
            console.log('[DEBUG] Script injection started');
           
            // Backup interval check
            const i = setInterval(()=>{
              if (window.turnstile) {
                console.log('[DEBUG] Dealing with turnstile');
                clearInterval(i);
                window.turnstile.render = (a,b) => {
                    let p = {
                        type: "TurnstileTaskProxyless",
                        websiteKey: b.sitekey,
                        websiteURL: window.location.href,
                        data: b.cData,
                        pagedata: b.chlPageData,
                        action: b.action,
                        userAgent: navigator.userAgent
                    }
                    console.log("Turnstile parameters:", JSON.stringify(p, null, 2));
                    window.tsCallback = b.callback;
                    return 'foo';
                }
              }
            },50);
            """
