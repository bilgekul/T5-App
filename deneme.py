from db import get_all_caching_data, set_caching_data, get_caching_data

# # Yeni bir çeviri ekleyin 
new_translation = {
    "english": "I am Bilgekul",
    "turkish": "Ben bilgekul"
 }

set_caching_data(new_translation)

# # Tüm çevirileri alın ve yazdırın
all_translations = get_all_caching_data()

print("All translations:")
for translation in all_translations:
   print(f'English: {translation["english"]}, Turkish: {translation["turkish"]}')

# Belirli bir çeviriyi alın ve yazdırın
specific_translation =  get_caching_data("Run.")
if specific_translation:
    print(f'\nSpecific translation:')
    print(f'English: {specific_translation["english"]}, Turkish: {specific_translation["turkish"]}')
else:
    print("\nSpecific translation not found.")
