
[num,txt,raw] = xlsread('000922.xlsx','2')


%[num,txt,raw] = xlsread('´Å°ô²âÊÔ6_120.xlsx','1ºÅ','A1:A52')
%V = num
%c = raw(:,[11,12])
%num('A:A')

B0 = num(10,[9])
V = num(:,[14])

B = num(:,[9])


%data = load('20191210.txt');
%B0 = data(1, 3)
%V = data(2:end, 1);
%I = data(2:end, 2);
%B = data(2:end, 3);

n = length(V)

n2 = length(B)

B = B - B0;

idx1 = (V > 0);
V1 = V(idx1);
B1 = B(idx1);

idx2 = (V < 0);
V2 = V(idx2);
B2 = B(idx2);

idx3 = (V==0);
V3 = B(idx3);
B3 = B(idx3);


figure(1);
plot(V1, B1, 'r-x');
hold on;
grid on;
plot(V2, B2, 'g-+');
plot(V3, B3, 'b-d');

plot(V1, B1, 'rx');
hold on;
grid on;
plot(V2, B2, 'g+');
plot(V3, B3, 'bd');

%===================
p = polyfit(V, B, 1);
Bfit = polyval(p, V);
plot(V, Bfit, 'y-');

detB = B - Bfit;
s = std(detB)

m = max(B)

A = s/m*100
%===================
pp = polyfit(V1, B1, 1);
Kp = pp(1);

B1fit = polyval(pp, V1);
detB1 = B1 - B1fit;

pm = polyfit(V2, B2, 1);
Km = pm(1);
B2fit = polyval(pm, V2);
detB2 = B2 - B2fit;
%===================
detbm = abs(Kp - Km)/(Kp+Km)/2*100


%=======================
minV = min(V);
maxV = max(V);
stepV = V(2) - V(1);
N = (maxV - minV)/stepV;

det_rec = zeros(N+1, 2);

for i = 0:N
    vi = minV + i*stepV;
    idx = (V > (vi - stepV/2) & V < (vi + stepV/2));
    Bi_rec = B(idx);
    a = max(Bi_rec);
    b = min(Bi_rec);
    
    det_rec(i+1, :) = [vi, a-b];
end
figure(2);
plot(det_rec(:, 1), det_rec(:, 2));
grid on;

detMax = max(det_rec(:,2));
BMax = max(B);
E = detMax/BMax*100


