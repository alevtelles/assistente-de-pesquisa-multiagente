from src.tools.tools import consulta_web, scrape_url, scrapping_url


# resultado = scrape_url.invoke(
#     "https://www.gee.gov.pt/pt/documentos/estudos-e-seminarios/temas-economicos/"
# )

# resultado = consulta_web.invoke(
#     "Últimas informações do uso de inteligência artificial para as condições climáticas"
# )

# print(resultado)

resultado = consulta_web.invoke(
    "What is the latest research on using AI for climate change mitigation?"
)
print(resultado)
