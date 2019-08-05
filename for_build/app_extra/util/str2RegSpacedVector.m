function x = str2RegSpacedVector(str)
x = cellfun(@(x) str2double(x),strsplit(str,' '));
x = x(1):x(2):x(3);
end
