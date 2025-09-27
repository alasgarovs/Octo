from src.info import (company_name, 
                  app_name, 
                  app_version, 
                  original_filename, 
                  file_description, 
                  legal_copyright)


def generate_md(output_path):
    version_content = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({app_version.replace('.', ',')}),
    mask=0x3f,
    flags=0x0,
    OS=0x4, 
    fileType=0x1, 
    subtype=0x0,
    date=(0, 0) 
    ),
  kids=[ 
    StringFileInfo( 
      [ 
      StringTable(
        u'040904b0',
        [StringStruct(u'CompanyName', u'{company_name}'),
        StringStruct(u'ProductName', u'{app_name}'),
        StringStruct(u'ProductVersion', u'{app_version}'),
        StringStruct(u'OriginalFilename', u'{original_filename}'),
        StringStruct(u'FileDescription', u'{file_description}'),
        StringStruct(u'LegalCopyright', u'{legal_copyright}'),])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(version_content.strip())



if __name__ == "__main__":
    generate_md('metadata.txt')
