# Qwen Coder için Prompt Şablonları

## ABAP Program Üretimi

```
You are an expert SAP ABAP developer with 15+ years of experience. 
Generate clean, efficient, and well-documented ABAP code following SAP best practices.

Task: Create an ABAP program for the following scenario:
{SCENARIO}

Requirements:
1. Use modern ABAP syntax (7.40+)
2. Include proper data declarations with appropriate types
3. Add comprehensive comments in English
4. Follow SAP security best practices (authority checks, input validation)
5. Include error handling with TRY-CATCH blocks
6. Use meaningful variable names (Hungarian notation: lv_, lt_, ls_)
7. Optimize for performance (avoid SELECT *, use appropriate indexes)
8. Include selection screen parameters if user interaction is needed

Output Format:
- Complete ABAP code ready for import
- Include program header with description
- Add form routines or methods for modularity
- Include ALV output if displaying data

Example Structure:
REPORT z_{program_name}.

*&---------------------------------------------------------------------*
*& Description: {description}
*& Author: AI Assistant
*& Date: {date}
*&---------------------------------------------------------------------*

Parameters: ...
Select-options: ...

START-OF-SELECTION.
  PERFORM main_process.

FORM main_process.
  " Implementation
ENDFORM.
```

## Function Module Üretimi

```
You are an expert SAP ABAP developer. Create a function module for:
{SCENARIO}

Requirements:
1. Function group: ZAI_AUTO_GENERATED
2. Short text describing the purpose
3. Import/Export/Tables/Exceptions parameters as needed
4. Proper documentation in function attributes
5. Error handling with BAPI_RETURN structure
6. Authority checks before data manipulation
7. Commit control (do not commit inside FM unless specified)

Interface:
FUNCTION Z_{FM_NAME}.
*"----------------------------------------------------------------------
*"*"Local Interface:
*"  IMPORTING
*"     VALUE({import_params}) TYPE  {type}
*"  EXPORTING
*"     VALUE({export_params}) TYPE  {type}
*"     VALUE(EX_RETURN) TYPE  BAPIRET2
*"  TABLES
*"      {table_params} STRUCTURE  {structure}
*"----------------------------------------------------------------------

" Implementation
ENDFUNCTION.
```

## ABAP Class Üretimi

```
Create an ABAP OO class for: {SCENARIO}

Design Requirements:
1. Follow SOLID principles
2. Use dependency injection where appropriate
3. Include interface definitions if needed
4. Add unit test class skeleton
5. Use visibility sections appropriately (PUBLIC/PROTECTED/PRIVATE)
6. Include method documentation
7. Use exception classes for error handling

Class Structure:
CLASS zcl_{class_name} DEFINITION
  PUBLIC
  FINAL
  CREATE PUBLIC.

  PUBLIC SECTION.
    INTERFACES: if_oo_adt_classrun.
    
    METHODS:
      constructor
        IMPORTING
          io_dependency TYPE REF TO if_dependency,
      {business_methods}.

  PROTECTED SECTION.
    DATA: {attributes}.

  PRIVATE SECTION.
    METHODS:
      {helper_methods}.

ENDCLASS.

CLASS zcl_{class_name} IMPLEMENTATION.
  " Method implementations
ENDCLASS.

" Test Class
CLASS ltc_{class_name}_test DEFINITION FINAL FOR TESTING
  DURATION SHORT
  RISK LEVEL HARMLESS.

  PRIVATE SECTION.
    DATA: cut TYPE REF TO zcl_{class_name}.
    METHODS:
      setup,
      {test_methods}.

ENDCLASS.
```

## Kod Analizi için Prompt

```
Analyze the following ABAP code for:
1. Performance issues (SELECT statements, loops, internal table operations)
2. Security vulnerabilities (SQL injection, authority checks, input validation)
3. Code quality (naming conventions, modularity, comments)
4. Syntax errors and warnings
5. Best practices violations

Provide:
- Line number for each issue
- Severity level (Critical/High/Medium/Low)
- Description of the problem
- Suggested fix with code example

ABAP Code to Analyze:
{CODE}

Output Format (JSON):
{
  "performance": [...],
  "security": [...],
  "quality": [...],
  "syntax": [...],
  "overall_score": 0-100,
  "recommendations": [...]
}
```

## RFC Entegrasyonu için Prompt

```
Create an ABAP program that integrates with external system via RFC.

Scenario: {SCENARIO}

Requirements:
1. Use SM59 RFC destination configuration
2. Implement both synchronous and asynchronous calls
3. Handle RFC exceptions properly
4. Log all RFC calls for audit
5. Implement retry mechanism for failed calls
6. Use tRFC/qRFC for guaranteed delivery if needed

Example Pattern:
DATA: lo_rfc_dest TYPE REF TO if_rfc_destination,
      lx_rfc_error TYPE REF TO cx_rfc_error.

TRY.
    lo_rfc_dest = cl_rfc_destination_provider=>get_destination(
      iv_name = 'DESTINATION_NAME' ).
      
    " RFC call
  CATCH cx_rfc_error INTO lx_rfc_error.
    " Error handling
ENDTRY.
```

## abapGit Serializasyonu için Prompt

```
Generate abapGit compatible XML serialization for:
Object Type: {OBJ_TYPE}
Object Name: {OBJ_NAME}

Requirements:
1. Follow abapGit XML format standards
2. Include all necessary metadata
3. Proper encoding (UTF-8)
4. Version control friendly (minimal diff noise)
5. Include .abapgit.xml manifest

Example Package File (.devc.xml):
<?xml version="1.0" encoding="utf-8"?>
<asx:abap xmlns:asx="http://www.sap.com/abapxml" version="1.0">
 <asx:values>
  <DATA>
   <MASTER_LANGUAGE>E</MASTER_LANGUAGE>
   <DEVELOPMENT_CLASS>Z{PACKAGE}</DEVELOPMENT_CLASS>
   <PACKAGE_TYPE>X</PACKAGE_TYPE>
  </DATA>
 </asx:values>
</asx:abap>
```
