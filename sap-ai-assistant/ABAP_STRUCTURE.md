# ABAP Git Repository Structure
# Bu dizin abapGit formatında ABAP objelerini içerir

## Paket Yapısı

```
src/
├── package.devc.xml          # Ana paket tanımı
├── zcl_ai_assistant.clas.abap    # AI Assistant Class
├── zcl_ai_assistant.clas.xml
├── zai_generate_report.prog.abap # Generate Report Program
├── zai_generate_report.prog.xml
├── zai_analyze_code.prog.abap    # Code Analysis Program
├── zai_analyze_code.prog.xml
└── ...

tests/
├── package.devc.xml
├── zcl_ai_assistant_test.clas.abap
└── zcl_ai_assistant_test.clas.xml

docs/
├── README.md
└── api_specification.md
```

## .abapgit.xml Örnek

```xml
<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <DATA>
   <MASTER_LANGUAGE>E</MASTER_LANGUAGE>
   <STARTING_FOLDER>/src/</STARTING_FOLDER>
   <FOLDER_LOGIC>FULL</FOLDER_LOGIC>
  </DATA>
 </asx:values>
</asx:abap>
```

## abapGit ile Kullanım

1. Repository'yi SAP'ye çekmek için:
```abap
" ABAPGit installation sonrası
CALL FUNCTION 'ZABAPGIT_START'
  EXPORTING
    iv_url = 'https://github.com/your-org/sap-ai-assistant-abap.git'.
```

2. Değişiklikleri push etmek için:
```bash
git add .
git commit -m "Add new AI generated objects"
git push origin main
```

## Obje Türleri

- **PROG**: ABAP Programları (REPORT)
- **CLAS**: ABAP Classes
- **FUNC**: Function Modules
- **INTF**: Interfaces
- **DEVC**: Development Packages
- **TABL**: Transparent Tables
- **DDLS**: CDS Views

## Naming Konvansiyonları

- Z* veya Y* namespace kullanılmalı
- AI tarafından üretilen objeler için: ZAI_*
- Test classları: ZCL_*_TEST
- Include programlar: Z*TOP, Z*UXX
