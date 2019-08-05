function prependFileToFile(file1, file2)
% Content of file1 prepended to the content of file2

tempFile = tempname(fileparts(file2));
copyfile(file2, tempFile);
copyfile(file1, file2);

ifid = fopen(tempFile, 'r');
if ifid == -1
    error('Could not open the file:\n%s', tempFile)
end

ofid = fopen(file2, 'a');
if ofid == -1
    error('Could not open the file:\n%s', file2)
end

while true
    s = fgetl(ifid);
    if ((numel(s) == 1) && (s == -1))
        break
    else
        fprintf(ofid, '\n%s', s);
    end
end
fclose(ifid);
fclose(ofid);
delete(tempFile);

end